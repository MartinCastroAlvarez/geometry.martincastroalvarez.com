"""
Pipeline steps: abstract Step and concrete step classes per StepName.

Title
-----
Steps Module

Context
-------
Each step is a unit of work for a Job. Steps are **idempotent**: given the same
job id and inputs, running the step multiple times must produce the same outcome
and must not duplicate side effects (e.g. creating the same child job twice).
Child job ids are derived from Signature(parent_job_id + step_name) so that
the same parent and step always yield the same child id; jobs are created
once and reused on retries. This allows the worker to safely retry messages
and avoids duplicate work or inconsistent state.

Step.run(**kwargs) returns a dict that is merged into job.stdout (keys may
overwrite); the step may mutate self.job (e.g. children_ids, status) and
the caller persists the updated job after run().
"""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from decimal import Decimal
from functools import cached_property
from typing import Any
from typing import Generator
from typing import Type

from attributes import Identifier
from attributes import Signature
from enums import Status
from enums import StepName
from exceptions import BridgeFailureError
from exceptions import ConvexComponentNotSimpleError
from exceptions import ConvexComponentOptimizationFailureError
from exceptions import EarClippingFailureError
from exceptions import GuardCoverageFailureError
from exceptions import GuardNotInComponentIdByPointError
from exceptions import OnlyMidpointsRemainingError
from exceptions import PolygonNotSimpleError
from exceptions import PolygonsDoNotShareEdgeError
from exceptions import StepNotHandledError
from exceptions import StitchWinnerSubsequenceError
from exceptions import ValidationError
from exceptions import ValidationObstacleNotContainedError
from geometry import Point
from geometry import Polygon
from geometry.convex import ConvexComponent
from geometry.ear import Ear
from geometry.polygon import _segments_intersect
from geometry.polygon import _segments_share_endpoint
from geometry.segment import Segment
from geometry.walk import Walk
from models import ArtGallery
from models import Job
from models import User
from repositories import JobsRepository
from settings import STITCH_BUCKET_SIZE
from structs import Collection
from structs import Table

logger = logging.getLogger(__name__)


class Step(ABC):
    """
    Abstract pipeline step. Receives a Job and user; run() returns a dict
    merged into job.stdout. Idempotent: given the same job and inputs, running
    multiple times must produce the same outcome and must not duplicate side effects.
    """

    def __init__(self, job: Job, user: User) -> None:
        self.job: Job = job
        self.user: User = user

    @cached_property
    def repository(self) -> JobsRepository:
        """JobsRepository for the step's user. Cached for the lifetime of the step instance."""
        return JobsRepository(user=self.user)

    @cached_property
    def parent(self) -> Job | None:
        """Parent job from repository, or None if this job has no parent."""
        if self.job.parent_id is None:
            return None
        return self.repository.get(self.job.parent_id)

    @staticmethod
    def of(step_name: StepName) -> Type[Step]:
        """
        Return the Step class for step_name. Raises StepNotHandledError if step name cannot be handled.

        Examples:
        >>> Step.of(StepName.ART_GALLERY) is ArtGalleryStep
        True
        >>> Step.of(StepName.EAR_CLIPPING) is EarClippingStep
        True
        >>> Step.of(StepName.VALIDATE_POLYGONS) is ValidationPolygonStep
        True
        """
        step_class_by_name: dict[StepName, Type[Step]] = {
            StepName.ART_GALLERY: ArtGalleryStep,
            StepName.VALIDATE_POLYGONS: ValidationPolygonStep,
            StepName.STITCHING: StitchingStep,
            StepName.EAR_CLIPPING: EarClippingStep,
            StepName.CONVEX_COMPONENT_OPTIMIZATION: ConvexComponentOptimizationStep,
            StepName.GUARD_PLACEMENT: GuardPlacementStep,
        }
        cls: Type[Step] | None = step_class_by_name.get(step_name)
        if cls is None:
            raise StepNotHandledError(f"Step cannot be handled: {step_name.slug}")
        return cls

    @abstractmethod
    def run(self, **kwargs: Any) -> dict[str, Any]:
        """
        Execute the step. Return a dict to merge into job.stdout.
        May mutate self.job (e.g. children_ids). Caller persists job after run().
        """
        raise NotImplementedError


class CoordinatorStep(Step):
    """Step that coordinates children: StartTask.broadcast() will START the first child."""

    @abstractmethod
    def run(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class SequenceStep(Step):
    """Step in a linear sequence: StartTask.broadcast() will START next sibling or REPORT parent if last."""

    @abstractmethod
    def run(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class MonitorStep(Step):
    """Step that monitors children: StartTask.broadcast() will START all children in batches."""

    @abstractmethod
    def run(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class ParallelStep(Step):
    """Step that runs in parallel with siblings: StartTask.broadcast() will REPORT parent."""

    @abstractmethod
    def run(self, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError


class ArtGalleryStep(CoordinatorStep):
    """
    Art gallery step: creates child jobs (validate_polygons, stitching, ear_clipping,
    convex_component_optimization, guard_placement) with deterministic ids. Children
    are created in PENDING status.
    Idempotent: same job and inputs yield the same children. run() ends with broadcast().

    Complexity: O(1).
    """

    def spawn(self) -> None:
        """
        Create child jobs (validate_polygons, stitching, ear_clipping, convex_component_optimization, guard_placement) with deterministic ids.
        Do NOT index children. Indexed jobs are available on the job list page.
        We do NOT want to see subtasks on the job list page.
        """
        child_step_names: list[StepName] = [
            StepName.VALIDATE_POLYGONS,
            StepName.STITCHING,
            StepName.EAR_CLIPPING,
            StepName.CONVEX_COMPONENT_OPTIMIZATION,
            StepName.GUARD_PLACEMENT,
        ]
        child_ids: list[Identifier] = []

        for step_name in child_step_names:
            child_id: Identifier = Identifier(Signature(f"{self.job.id}_{step_name.value}"))
            if self.repository.exists(child_id):
                child_ids.append(child_id)
                continue
            child: Job = Job(
                id=child_id,
                parent_id=self.job.id,
                status=Status.PENDING,
                step_name=step_name,
                stdin=dict(self.job.stdin),
            )
            self.repository.save(child)
            child_ids.append(child_id)

            # NOTE: Do NOT index children.
            # index: JobsPrivateIndex = JobsPrivateIndex(user_email=self.user.email)
            # index.save(
            #     Indexed(
            #         index_id=Identifier(Countdown.from_timestamp(child.created_at)),
            #         real_id=child.id,
            #     )
            # )

        self.job.children_ids = child_ids

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.spawn()
        logger.info("ArtGalleryStep.run() | job.id=%s children=%s", self.job.id, len(self.job.children_ids))
        return {
            "boundary": self.job.stdin.get("boundary"),
            "obstacles": self.job.stdin.get("obstacles"),
        }


class ValidationPolygonStep(SequenceStep):
    """
    Validates boundary and obstacles using api/geometry (same logic as lab ArtGallery.validate()).
    Parses boundary and obstacles via Polygon.unserialize(); let it throw. On success returns step
    result and calls broadcast(). We do not catch Exception; let failures raise so StartTask handles them.

    Complexity: O(n^2), n = total vertices (boundary + all obstacles).
    """

    boundary: Polygon | None
    obstacles: list[Polygon]

    def __init__(self, job: Job, user: User) -> None:
        super().__init__(job, user)
        self.boundary: Polygon | None = None
        self.obstacles: list[Polygon] = []

    def validate_simplicity(self) -> None:
        """
        Ensure boundary and every obstacle are simple (degree 2, no self-intersection).
        Required so later steps (ear clipping, stitching) operate on well-defined polygons.
        """
        if not self.boundary.is_simple():
            raise PolygonNotSimpleError("Boundary polygon is not simple.")
        if any(not obstacle.is_simple() for obstacle in self.obstacles):
            raise PolygonNotSimpleError("Obstacle polygon is not simple.")

    def validate_orientation(self) -> None:
        """
        Ensure boundary is CCW (outer ring) and every obstacle is CW (hole).
        Convention required for containment tests and stitching (bridge/merge logic).
        """
        self.boundary.sort("ccw")
        for obstacle in self.obstacles:
            obstacle.sort("cw")

    def validate_containment(self) -> None:
        """
        Ensure every obstacle vertex lies strictly inside the boundary.
        Obstacles must be holes fully enclosed by the outer polygon for valid stitching.
        """
        if any(not all(self.boundary.contains(point, inclusive=False) for point in obstacle) for obstacle in self.obstacles):
            raise ValidationObstacleNotContainedError(f"Obstacle is not strictly inside the boundary ({self.boundary}).")

    def validate_intersections(self) -> None:
        """
        Ensure no invalid contact: obstacle edges must not cross/touch boundary edges
        (except at shared vertices), no obstacle vertex on a boundary edge, and no
        two obstacles may intersect or touch. Prevents ambiguous topology for bridging.
        """
        if any(
            _segments_intersect(edge, boundary_edge, inclusive=True) and not _segments_share_endpoint(edge, boundary_edge)
            for obstacle in self.obstacles
            for edge in obstacle.edges
            for boundary_edge in self.boundary.edges
        ):
            raise PolygonNotSimpleError("Obstacle edge intersects or touches boundary.")
        if any(
            boundary_edge.contains(point, inclusive=True)
            for obstacle in self.obstacles
            for point in obstacle
            for boundary_edge in self.boundary.edges
        ):
            raise PolygonNotSimpleError("Obstacle has a vertex on the boundary.")
        if any(obstacle.intersects(other, inclusive=True) for obstacle in self.obstacles for other in self.obstacles if obstacle != other):
            raise PolygonNotSimpleError("Obstacles intersect or touch.")

    def run(self, **kwargs: Any) -> dict[str, Any]:
        gallery: ArtGallery = ArtGallery.unserialize(self.job.stdin)
        self.boundary = gallery.boundary
        self.obstacles = list(gallery.obstacles)
        self.validate_simplicity()
        self.validate_orientation()
        self.validate_containment()
        self.validate_intersections()
        logger.info("ValidationPolygonStep.run() | job.id=%s obstacles=%s", self.job.id, len(self.obstacles))
        return {
            "boundary": self.boundary.serialize(),
            "obstacles": [obstacle.serialize() for obstacle in self.obstacles],
        }


class StitchingStep(SequenceStep):
    """
    Stitching step: merges boundary and obstacles into a single polygon (stitched)
    by sorting obstacles by rightmost vertex and bridging each to the current outer
    polygon. Same logic as lab ArtGallery.points. Idempotent: same job and inputs
    yield the same stitched polygon. Emits "stitched" (serialized Polygon) and
    "stitches" (list of serialized bridge Segment) in stdout.

    Performance optimization: we iterate polygon points starting from the rightmost
    (using Sequence shift from structs.py; one O(n) rotation per obstacle). We keep
    a bucket of the shortest STITCH_BUCKET_SIZE valid bridges; once the bucket is
    full we pick the smallest by size and stop, avoiding full O(n) checks when good
    short bridges exist.

    Complexity: O(n^3), n = total vertices (boundary + all obstacles); bucket early exit often reduces work.
    """

    boundary: Polygon
    obstacles: list[Polygon]
    points: Polygon

    def sort(self) -> None:
        """Sort obstacles in place by rightmost vertex (x, y) descending for bridge order."""
        self.obstacles.sort(key=lambda obstacle: (obstacle.rightmost.x, obstacle.rightmost.y), reverse=True)

    def run(self, **kwargs: Any) -> dict[str, Any]:
        gallery: ArtGallery = ArtGallery.unserialize(self.job.stdout)
        self.boundary = gallery.boundary
        self.obstacles = list(gallery.obstacles)

        # No obstacles: stitched result is the boundary; no bridge edges added.
        if not self.obstacles:
            self.points = self.boundary
            logger.info("StitchingStep.run() | job.id=%s boundary_points=%s", self.job.id, len(self.boundary))
            return {"stitched": self.points.serialize(), "stitches": []}

        # Sort obstacles by rightmost vertex (desc) and init working polygon and its edges.
        self.sort()
        logger.info("StitchingStep.run() | job.id=%s obstacles=%s boundary_points=%s", self.job.id, len(self.obstacles), len(self.boundary))
        stitched: Polygon = Polygon(list(self.boundary))
        stitches: list[Segment] = []

        for obstacle in self.obstacles:
            obstacle.sort("cw")
            bridge: Segment | None = None
            anchor: Point | None = None

            # Find valid bridge from polygon to obstacle anchor (bucket of candidates).
            i: int = 0
            for anchor in obstacle:
                bridge = None

                for candidate in stitched << stitched.rightmost:

                    # Exit early if the candidate is the anchor.
                    if candidate == anchor:
                        continue

                    segment: Segment = candidate.to(anchor)

                    # Exit early if the segment is not contained in the boundary.
                    if not self.boundary.contains(segment, inclusive=True):
                        continue

                    # Exit early if the segment intersects any other obstacle.
                    if any(other.intersects(segment, inclusive=False) for other in self.obstacles if other is not obstacle):
                        continue

                    # Exit early if the segment crosses the current obstacle (except at anchor).
                    if any(segment.crosses(edge) for edge in obstacle.edges):
                        continue

                    # Exit early if the segment is collinear with any boundary edge.
                    if any(
                        Walk(start=edge[0], center=edge[1], end=segment[0]).is_collinear()
                        and Walk(start=edge[0], center=edge[1], end=segment[1]).is_collinear()
                        for edge in self.boundary.edges
                        if not _segments_share_endpoint(edge, segment)
                    ):
                        continue

                    # Exit early if the segment intersects any other segment.
                    if any(segment.crosses(edge) for edge in stitched.edges):
                        continue

                    # Exit early if the bucket is full.
                    # Optimization: It might not be the shortest, but who cares...
                    if i >= STITCH_BUCKET_SIZE:
                        break

                    # Candidate is bucket-eligible; count it.
                    i += 1
                    # Track the shortest segment among candidates seen so far.
                    if bridge is None or segment.size < bridge.size:
                        bridge = segment

                # Exit early if a bridge is found.
                if bridge is not None:
                    break

            if bridge is None or anchor is None:
                raise BridgeFailureError(f"No valid bridge found for obstacle: {obstacle}")

            # Reject if bridge is a contiguous subsequence of polygon or obstacle (cannot stitch).
            vertex: Point = bridge[0]
            if bridge in stitched:
                raise StitchWinnerSubsequenceError("Winner is a subsequence of boundary points; cannot stitch")
            if bridge in obstacle:
                raise StitchWinnerSubsequenceError("Winner is a subsequence of obstacle; cannot stitch")

            # Rotate polygon so vertex is last, obstacle so anchor is first; require CCW/CW; merge and update.

            left: Polygon = Polygon(list(stitched))
            right: Polygon = Polygon(list(obstacle))

            left.sort("ccw")
            right.sort("cw")

            left = left >> vertex
            right = right << anchor

            assert right[0] == anchor, f"Right polygon does not start with anchor: {right}"
            assert left[-1] == vertex, f"Left polygon does not end with vertex: {left}"

            # Update the stitched polygon after adding the bridge.
            merged: list[Point] = list(left) + list(right) + [anchor, vertex]
            stitched = Polygon(merged)
            stitches.append(bridge)

        assert stitched.is_ccw(), f"Stitched polygon is not CCW: {stitched}"
        self.points = stitched
        logger.info("StitchingStep.run() | job.id=%s stitched_points=%s bridge_edges=%s", self.job.id, len(self.points), len(stitches))
        return {"stitched": self.points.serialize(), "stitches": [stitch.serialize() for stitch in stitches]}


class EarClippingStep(SequenceStep):
    """
    Ear clipping step. Reads stitched polygon from job.stdout (from stitching step).
    Runs ear clipping only; returns ears as Table.serialize().
    Polygon.unserialize() raises if stitched is missing or invalid.
    Rejects any ear whose segments (vertex–vertex or vertex–edge-midpoint) cross an obstacle,
    so that downstream steps can assume components are obstacle-safe.

    Complexity: O(n^3), n = number of vertices of the stitched polygon.
    """

    gallery: ArtGallery

    def clip(self, titanic: Polygon) -> Generator[Ear, None, None]:
        # Enforce global CCW once so ear detection, diagonal tests, and final merge are consistent.
        titanic.sort("ccw")
        logger.debug("EarClippingStep.clip() | job.id=%s polygon_vertices=%s", self.job.id, len(titanic))

        # Ear clipping: while polygon has more than 3 vertices, find and clip an ear.
        found: bool = True
        while len(titanic) > 3 and found:
            logger.debug("EarClippingStep.clip() | job.id=%s remaining_vertices=%s", self.job.id, len(titanic))
            n: int = len(titanic)
            found = False
            for j in range(n):

                # Only clip if we would leave at least 3 vertices (the last 3 are the final triangle).
                # Check if the triangle is a valid ear.
                walk: Walk = Walk(start=titanic[j - 1], center=titanic[j], end=titanic[j + 1])

                # CW ears are not valid because they contain empty space.
                if walk.is_cw() or walk.is_collinear():
                    continue

                # Build the ear from the CCW walk.
                # walk = walk if walk.is_ccw() else ~walk
                ear = Ear(list(walk))

                # The ear must be fully inside the boundary.
                if not titanic.contains(ear.diagonal.midpoint, inclusive=True):
                    continue

                # The ear must not contain any other vertices.
                excluded = ((j - 1) % n, j, (j + 1) % n)
                if any(ear.contains(titanic[k], inclusive=False) for k in range(n) if k not in excluded):
                    continue

                # The ear diagonal midpoint must not be inside any obstacle.
                # if any(obstacle.contains(ear.diagonal.midpoint, inclusive=False) for obstacle in self.gallery.obstacles):
                #     continue

                # The ear diagonal must not cross any obstacle edges.
                # if any(any(ear.diagonal.crosses(obs_edge) for obs_edge in obstacle.edges) for obstacle in self.gallery.obstacles):
                #     continue

                # Add the ear to the table.
                yield ear

                # Remove ear tip from polygon by index (position), not by point value;
                # the same point may appear at other indices and must be kept.
                titanic.pop(j)

                # Continue searching for an ear.
                found = True
                break

        logger.debug("EarClippingStep.clip() | job.id=%s final_triangle_vertices=%s", self.job.id, len(titanic))
        # The remainder should contain exactly 3 vertices.
        # If there are more than 3 vertices, then it means there
        # is a problem in the ear clipping step above, not here.
        # Some iteration failed to detect an ear propertly.
        if len(titanic) != 3:
            return
            # raise EarClippingFailureError(
            #     f"Expected 3 vertices or less; got {len(titanic)}."
            #     f"The (remaining) polygon is: {titanic}."
            #     f"The ears found so far are: {self.gallery.ears}."
            # )

        # Add final triangle as last ear (ccw or reversed if cw).
        path: Walk = Walk(start=titanic[0], center=titanic[1], end=titanic[2])
        if path.is_ccw():
            ear = Ear([titanic[0], titanic[1], titanic[2]])
            ear.sort("ccw")
            logger.debug("EarClippingStep.clip() | job.id=%s final_ear tip=%s", self.job.id, titanic[1])
            yield ear

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.gallery = ArtGallery.unserialize(self.job.stdout)
        self.gallery.ears = Table()
        for ear in self.clip(Polygon(list(self.gallery.stitched))):
            self.gallery.ears.add(ear)

        for obs in self.gallery.obstacles:
            for ear in self.gallery.ears:
                if any(ear.diagonal.crosses(edge) for edge in obs.edges):
                    raise EarClippingFailureError(f"Ear diagonal crosses obstacle edge: {ear.diagonal} crosses {obs.edges}")

        if not self.gallery.ears:
            raise EarClippingFailureError("No ears found for polygon")
        logger.info("EarClippingStep.run() | job.id=%s ears=%s", self.job.id, len(self.gallery.ears))
        return {"ears": self.gallery.ears.serialize()}


class ConvexComponentOptimizationStep(SequenceStep):
    """
    Convex component optimization step. Reads ears from job.stdout (from ear clipping step).
    Merges adjacent convex components; returns convex_components as Table.serialize().
    Ear.unserialize() raises if ears data is missing or invalid.

    Assumes ears do not intersect obstacles (enforced by ear clipping and unit tests).
    Since ears are convex and obstacle-safe, merging two adjacent convex components
    yields a convex component that does not intersect any obstacle.

    Complexity: O(n^3), n = number of ears (triangles), on the order of stitched vertices.
    """

    gallery: ArtGallery

    def build_adjacency_table(self, table: Table[ConvexComponent]) -> Table[Collection[ConvexComponent, Identifier]]:
        """
        Build Table[Collection[ConvexComponent, Identifier]] from Table[ConvexComponent]: index by edge,
        then for each component create a collection and add ids of components sharing an edge.
        Serializes as dict mapping component id -> list of adjacent component ids.
        """
        components_by_edge: defaultdict[Segment, list[ConvexComponent]] = defaultdict(list)
        for component in table:
            for edge in component.edges:
                components_by_edge[edge].append(component)
        result: Table[Collection[ConvexComponent, Identifier]] = Table()
        for component in table:
            collection: Collection[ConvexComponent, Identifier] = Collection(component)
            for edge in component.edges:
                for other in components_by_edge[edge]:
                    if other is not component:
                        collection += other.id
            result.add(collection)
        return result

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.gallery = ArtGallery.unserialize(self.job.stdout)
        ears: Table[Ear] = self.gallery.ears
        components_table: Table[ConvexComponent] = Table.unserialize([ConvexComponent(ear) for ear in ears])
        adjacency_table: Table[Collection[ConvexComponent, Identifier]] = self.build_adjacency_table(components_table)
        logger.info("ConvexComponentOptimizationStep.run() | job.id=%s components=%s", self.job.id, len(components_table))

        # Merge adjacent pairs by largest area until no merge possible.
        while True:
            logger.debug("ConvexComponentOptimizationStep.run() | job.id=%s components=%s", self.job.id, len(components_table))
            best_area: Decimal | None = None
            best_merge: ConvexComponent | None = None
            best_pair: tuple[ConvexComponent, ConvexComponent] | None = None
            for component in components_table:
                for adjacent_id in adjacency_table[component]:
                    adjacent: ConvexComponent = components_table[adjacent_id]
                    try:
                        merge: ConvexComponent = component + adjacent
                    except (ValidationError, ConvexComponentNotSimpleError, PolygonsDoNotShareEdgeError):
                        continue
                    if best_area is None or abs(merge.signed_area) > best_area:
                        best_area = abs(merge.signed_area)
                        best_merge = merge
                        best_pair = (component, adjacent)

            # When no merge occurs, it is time to stop.
            if best_pair is None or best_merge is None:
                logger.debug("ConvexComponentOptimizationStep.run() | job.id=%s no_merge_candidate stopping", self.job.id)
                break

            # Merge the best pair, and update the tables.
            logger.debug(
                "ConvexComponentOptimizationStep.run() | job.id=%s merging pair id_a=%s id_b=%s merged_area=%s components_before=%s",
                self.job.id,
                best_pair[0].id,
                best_pair[1].id,
                best_area,
                len(components_table),
            )
            components_table -= best_pair[0]
            components_table -= best_pair[1]
            components_table += best_merge
            adjacency_table = self.build_adjacency_table(components_table)

        logger.info("ConvexComponentOptimizationStep.run() | job.id=%s components_after_merges=%s", self.job.id, len(components_table))
        if len(components_table) == 0:
            raise ConvexComponentOptimizationFailureError("No convex components found")
        return {"convex_components": components_table.serialize(), "adjacency": adjacency_table.serialize()}


class GuardPlacementStep(SequenceStep):
    """
    Guard placement step. Reads stitched, convex_components and adjacency from job.stdout.
    Boundary and obstacles come from stdout (merged from validation).

    Algorithm (same greedy logic with exploration heuristic for performance):
    1. Remaining state: all convex components and all stitched points (vertices to cover).
    2. Sort remaining components by measure(component): fewest points not in remaining first (most uncovered points).
    3. Pick the first component; its vertices are the guard candidates.
    4. Score each candidate via explore(guard): returns a Collection of points visible from that guard.
       explore uses component_id_by_point to find all components the guard belongs to, hydrates
       visibility_by_segment and the visibility bag with all points of those components, then
       explorable = adjacent of those components; only adds adjacent-of-adjacent when the current
       component yielded at least one visible point.
    5. Best guard = candidate that sees the most remaining points (using explore). Add that guard and
       its full visibility (all stitched points seen) to the gallery; remove the largest component
       and any other component fully covered; remove from remaining points all points that guard sees.
    6. Repeat until no points remain.

    explore(guard): gets guard's component ids from component_id_by_point; initializes explored with
    those ids and hydrates visibility + visibility_by_segment with all points of those components;
    explorable = union of adjacency of those components. While explorable - explored non-empty:
    take an adjacent component, add to explored, compute visibility of its points via sees(), add
    visible to bag; if at least one visible, add its adjacent to explorable. Returns the bag.

    Returns guards and visibility as Table.serialize().

    Complexity: O(n^4) in the worst case; the exploration heuristic reduces visibility checks in practice.
    """

    gallery: ArtGallery
    component_id_by_point: Table[Collection[Point, Identifier]]
    visibility_by_segment: dict[Segment, bool]
    remaining_points: set[Point]
    remaining_components: set[ConvexComponent]
    component_id_by_midpoint: dict[Point, Identifier]

    def measure(self, convex_component: ConvexComponent) -> int:
        """Return the number of points (vertices and edge midpoints) of the component that are not in self.remaining_points."""
        points: list[Point] = list(convex_component) + [edge.midpoint for edge in convex_component.edges]
        return len([p for p in points if p not in self.remaining_points])

    def explore(self, guard: Point) -> Collection[Point, Point]:
        """
        Return a Collection(guard) of points visible from guard. Uses component_id_by_point to find
        all components the guard belongs to; hydrates visibility_by_segment and the visibility
        collection with all points of those components. Then expands via adjacent components; only
        adds adjacent-of-adjacent to explorable when the current component yielded at least
        one visible point.
        """
        visibility: Collection[Point, Point] = Collection(guard)

        if hash(guard) not in self.component_id_by_point:
            raise GuardNotInComponentIdByPointError("Guard not in component_id_by_point; invalid state (prepare() not run or guard not a vertex).")

        # Record the components that are already visible due to being a vertex of the guard's component.
        explored: set[Identifier] = set(self.component_id_by_point[guard])
        explorable: set[Identifier] = {
            adj_id for component_id in explored for adj_id in self.gallery.adjacency[self.gallery.convex_components[component_id]].items
        }

        # Hydrate visibility with all points of every component the guard belongs to.
        # Use sees() for each point so that segments that leave the boundary (e.g. chords across
        # spikes in a non-convex boundary) or cross obstacles are not counted as visible.
        for component_id in explored:
            component: ConvexComponent = self.gallery.convex_components[component_id]
            for point in component:
                if self.sees(guard, point):
                    visibility += point
            for edge in component.edges:
                if self.sees(guard, edge.midpoint):
                    visibility += edge.midpoint

        # Continue exploring explorable components until no more are available.
        while explorable - explored:

            # Find the adjacent component to explore.
            adjacent_id: Identifier = (explorable - explored).pop()
            logger.debug("GuardPlacementStep.explore() | job.id=%s adjacent_id=%s explored=%s", self.job.id, adjacent_id, len(explored))
            adjacent: ConvexComponent = self.gallery.convex_components[adjacent_id]

            # Mark the component as explored.
            explored.add(adjacent_id)
            visible = False
            for point in adjacent:
                if self.sees(guard, point):
                    visibility += point
                    visible = True
            for midpoint in adjacent.midpoints:
                if self.sees(guard, midpoint):
                    visibility += midpoint
                    visible = True

            # If the component is visible, explore its adjacent components.
            if visible:
                explorable.update(self.gallery.adjacency[adjacent])

        return visibility

    def sees(self, guard: Point, target: Point) -> bool:
        """
        True if target is visible from guard in the art gallery. Uses self.gallery. Caches by segment in visibility_by_segment.
        If both points belong to the same convex component, they are visible.
        """

        # If the guard and target are the same, they are visible.
        if guard == target:
            return True

        # Check if the segment has already been evaluated (explore() pre-fills same-component segments).
        segment: Segment = guard.to(target)
        if segment in self.visibility_by_segment:
            return self.visibility_by_segment[segment]

        # Segment must lie entirely inside the boundary (endpoints, midpoint, no interior crossing).
        if not self.gallery.boundary.contains(segment, inclusive=True):
            self.visibility_by_segment[segment] = False
            return False

        # Check if the segment intersects any obstacles (must not cross an obstacle edge in the interior).
        for obstacle in self.gallery.obstacles:

            # Exit early: segment is inside the obstacle.
            if obstacle.intersects(segment.midpoint, inclusive=False):
                self.visibility_by_segment[segment] = False
                return False

            for edge in obstacle.edges:
                if segment.crosses(edge):
                    self.visibility_by_segment[segment] = False
                    return False

        # The segment is visible if no checks failed.
        self.visibility_by_segment[segment] = True
        return True

    def prepare(self) -> None:
        """
        Hydrate self.component_id_by_point: for each convex component and each point in it,
        map the point to that component's id. Points on shared edges appear in multiple components.
        """
        self.gallery.coverage = set(self.gallery.stitched)
        self.component_id_by_point = Table()
        for component in self.gallery.convex_components:
            for point in component:
                if point not in self.component_id_by_point:
                    self.component_id_by_point.add(Collection(point))
                self.component_id_by_point[point] += component.id
            for midpoint in component.midpoints:
                self.component_ids_by_midpoint[midpoint].add(component.id)
                self.gallery.coverage.add(midpoint)

    def compete(self, candidates: list[Point]) -> (Point, Collection[Point, Point]):
        """
        Return the best candidate and its visibility.

        candidates: list[Point] - The candidates to compete.

        Returns:
            Point: The best candidate.
            Collection[Point, Point]: The visibility of the best candidate.
        """
        assert len(candidates) > 0, f"GuardPlacementStep.compete() | job.id={self.job.id} candidates={candidates}"
        visibility_by_guard: dict[Point, Collection[Point, Point]] = {guard: self.explore(guard) for guard in candidates}
        coverage_by_guard: dict[Point, int] = {
            guard: sum(1 for point in self.remaining_points if point in visibility_by_guard[guard]) for guard in candidates
        }
        key = lambda guard: (coverage_by_guard[guard], len(visibility_by_guard[guard]), hash(guard))
        sorted_candidates: list[Point] = sorted(candidates, key=key, reverse=True)
        return sorted_candidates[0], visibility_by_guard[sorted_candidates[0]]

    def analyze(self) -> None:
        """
        Build exclusivity table: for each guard, points visible only by that guard (not covered by any other guard).
        Sets self.gallery.exclusivity. Raises GuardHasNoExclusivityError if any guard has no exclusive points.
        """
        visibility: list[Collection[Point, Point]] = list(self.gallery.visibility.values())
        self.gallery.exclusivity = Table()
        for guard in list(self.gallery.guards):
            visibility: Collection[Point, Point] = self.gallery.visibility[guard]
            other_points: set[Point] = {point for other in self.gallery.guards.values() if other != guard for point in self.gallery.visibility[other].items}
            exclusive: set[Point] = set(visibility.items) - other_points
            if not exclusive:
                self.gallery.guards -= guard
                self.gallery.visibility -= guard
                continue
            exclusivity: Collection[Point, Point] = Collection(guard)
            for point in exclusive:
                exclusivity += point
            self.gallery.exclusivity += exclusivity

    def propose(self, max_candidates: int = 10) -> list[Point]:
        """
        Return the candidates to compete.
        It reduces the number of explore() calls later in self.compete().

        Returns:
            list[Point]: The candidates to compete.
        """
        if not self.remaining_components:
            raise OnlyMidpointsRemainingError("Only midpoints remain.")
        key = lambda c: (self.measure(c), len(c), c.id)
        sorted_components: list[ConvexComponent] = sorted(self.remaining_components, key=key)
        largest_component: ConvexComponent = sorted_components[0]
        return list(largest_component)[:max_candidates]

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.gallery = ArtGallery.unserialize(self.job.stdout)
        self.visibility_by_segment = {}
        self.component_ids_by_midpoint = defaultdict(set)
        self.component_id_by_point = Table()

        self.prepare()

        self.remaining_points = set(self.gallery.coverage)
        self.remaining_components = set(self.gallery.convex_components)

        # Run until all points are covered.
        while self.remaining_points:
            logger.debug(
                "GuardPlacementStep.run() | job.id=%s points_remaining=%s components_remaining=%s",
                self.job.id,
                len(self.remaining_points),
                len(self.remaining_components),
            )

            # Find the best candidates to compete.
            # Sometimes only midpoints remain, even though they are not valid candidates.
            # We need to propose candidates that are in the same components as the remaining points.
            try:
                candidates: list[Point] = self.propose()
            except OnlyMidpointsRemainingError:
                candidates: set[Point] = [
                    self.gallery.convex_components[component_id][0]
                    for midpoint in self.remaining_points
                    for component_id in self.component_ids_by_midpoint[midpoint]
                ]
                candidates: list[Point] = list(candidates)

            # Add the best guard and its visibility to the gallery.
            # Remove the component and the points from the remaining sets.
            best_guard, best_visibility = self.compete(candidates)
            self.gallery.guards += best_guard
            self.gallery.visibility += best_visibility
            assert len(best_visibility) > 0, f"GuardPlacementStep.run() | job.id={self.job.id} best_visibility={best_visibility}"
            self.remaining_points -= set(best_visibility)

            # Remove any component fully covered by best_guard using best_visibility (avoids redundant sees() calls).
            # This should already include the best_component, but we'll be safe and remove it anyway.
            # The guard was placed inside the `best_component`, so it is guaranteed to be covered by the best_visibility.
            # However, we don't explicitely remove it here, just to make sure the following code works.
            for component in list(self.remaining_components):
                if any(point in self.remaining_points for point in component):
                    continue
                if any(midpoint in self.remaining_points for midpoint in component.midpoints):
                    continue
                self.remaining_components -= {component}
            logger.info("GuardPlacementStep.run() | job.id=%s points_remaining=%s", self.job.id, len(self.remaining_points))

        logger.info("GuardPlacementStep.run() | job.id=%s guards=%s", self.job.id, len(self.gallery.guards))
        if len(self.gallery.guards) == 0:
            raise GuardCoverageFailureError("No guards placed")
        assert not self.remaining_components, "Remaining components should be empty."
        assert not self.remaining_points, "Remaining points should be empty."

        self.analyze()

        return {
            "guards": self.gallery.guards.serialize(),
            "visibility": self.gallery.visibility.serialize(),
            "exclusivity": self.gallery.exclusivity.serialize(),
            "coverage": [p.serialize() for p in self.gallery.coverage],
        }
