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
from exceptions import EarClippingFailureError
from exceptions import GuardCoverageFailureError
from exceptions import GuardNotInComponentIdByPointError
from exceptions import PolygonNotSimpleError
from exceptions import PolygonsDoNotShareEdgeError
from exceptions import StepNotHandledError
from exceptions import StitchWinnerSubsequenceError
from exceptions import ValidationBoundaryNotCCWError
from exceptions import ValidationError
from exceptions import ValidationObstacleNotContainedError
from exceptions import ValidationObstacleNotCWError
from geometry import Point
from geometry import Polygon
from geometry.convex import ConvexComponent
from geometry.ear import Ear
from geometry.segment import Segment
from geometry.walk import Walk
from models import ArtGallery
from models import Job
from models import User
from repositories import JobsRepository
from settings import STITCH_BUCKET_SIZE
from structs import Bag
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

    def __init__(self, job: Job, user: User) -> None:
        super().__init__(job, user)
        self.boundary: Polygon | None = None
        self.obstacles: list[Polygon] = []

    def validate_simplicity(self) -> None:
        """
        Ensure boundary and every obstacle are simple (degree 2, no self-intersection).
        Required so later steps (ear clipping, stitching) operate on well-defined polygons.
        """
        assert self.boundary is not None
        if not self.boundary.is_simple():
            raise PolygonNotSimpleError("Boundary polygon is not simple.")
        if any(not obstacle.is_simple() for obstacle in self.obstacles):
            raise PolygonNotSimpleError("Obstacle polygon is not simple.")

    def validate_orientation(self) -> None:
        """
        Ensure boundary is CCW (outer ring) and every obstacle is CW (hole).
        Convention required for containment tests and stitching (bridge/merge logic).
        """
        assert self.boundary is not None
        self.boundary.sort("ccw")
        if not self.boundary.is_ccw():
            raise ValidationBoundaryNotCCWError()
        for obstacle in self.obstacles:
            obstacle.sort("cw")
        if any(not obstacle.is_cw() for obstacle in self.obstacles):
            raise ValidationObstacleNotCWError()

    def validate_containment(self) -> None:
        """
        Ensure every obstacle vertex lies strictly inside the boundary.
        Obstacles must be holes fully enclosed by the outer polygon for valid stitching.
        """
        assert self.boundary is not None
        if any(not all(self.boundary.contains(point, inclusive=False) for point in obstacle) for obstacle in self.obstacles):
            raise ValidationObstacleNotContainedError(f"Obstacle is not strictly inside the boundary ({self.boundary}).")

    def validate_intersections(self) -> None:
        """
        Ensure no invalid contact: obstacle edges must not cross/touch boundary edges
        (except at shared vertices), no obstacle vertex on a boundary edge, and no
        two obstacles may intersect or touch. Prevents ambiguous topology for bridging.
        """
        assert self.boundary is not None
        if any(
            edge.intersects(boundary_edge, inclusive=True) and not edge.connects(boundary_edge)
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

    def __init__(self, job: Job, user: User) -> None:
        super().__init__(job, user)
        self.boundary: Polygon | None = None
        self.obstacles: list[Polygon] = []
        self.points: Polygon | None = None

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
        assert self.boundary is not None
        logger.info("StitchingStep.run() | job.id=%s obstacles=%s boundary_points=%s", self.job.id, len(self.obstacles), len(self.boundary))
        points: Polygon = Polygon(list(self.boundary))
        edges: list[Segment] = list(points.edges)
        stitches: list[Segment] = []

        for obstacle in self.obstacles:
            obstacle.sort("cw")
            bridge: Segment | None = None
            anchor: Point | None = None

            # Find valid bridge from polygon to obstacle anchor (bucket of candidates).
            i: int = 0
            for anchor in obstacle:
                bridge = None

                for candidate in points << points.rightmost:

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
                    if any(
                        not segment.connects(edge) and segment.intersects(edge, inclusive=False)
                        for edge in obstacle.edges
                    ):
                        continue

                    # Exit early if the segment is collinear with any boundary edge.
                    if any(
                        Walk(start=edge[0], center=edge[1], end=segment[0]).is_collinear()
                        and Walk(start=edge[0], center=edge[1], end=segment[1]).is_collinear()
                        for edge in self.boundary.edges
                        if not edge.connects(segment)
                    ):
                        continue

                    # Exit early if the segment intersects any other segment.
                    if any(edge.intersects(segment, inclusive=False) for edge in edges if not edge.connects(segment)):
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
            if bridge in points:
                raise StitchWinnerSubsequenceError("Winner is a subsequence of boundary points; cannot stitch")
            if bridge in obstacle:
                raise StitchWinnerSubsequenceError("Winner is a subsequence of obstacle; cannot stitch")

            # Rotate polygon so vertex is last, obstacle so anchor is first; require CCW/CW; merge and update.
            stitches.append(bridge)
            left: Polygon = Polygon(list(points >> vertex))
            right: Polygon = Polygon(list(obstacle << anchor))
            if not left.is_ccw():
                raise StitchWinnerSubsequenceError("Left is not CCW; cannot stitch")
            if not right.is_cw():
                raise StitchWinnerSubsequenceError("Right is not CW; cannot stitch")
            merged: list[Point] = list(left) + list(right) + [anchor, vertex]
            points = Polygon(merged)
            edges = list(points.edges)

        points.sort("ccw")
        self.points = points
        logger.info("StitchingStep.run() | job.id=%s stitched_points=%s bridge_edges=%s", self.job.id, len(self.points), len(stitches))
        return {"stitched": self.points.serialize(), "stitches": [stitch.serialize() for stitch in stitches]}


class EarClippingStep(SequenceStep):
    """
    Ear clipping step. Reads stitched polygon from job.stdout (from stitching step).
    Runs ear clipping only; returns ears as Table.serialize().
    Polygon.unserialize() raises if stitched is missing or invalid.

    Complexity: O(n^3), n = number of vertices of the stitched polygon.
    """

    def clip(self, titanic: Polygon) -> Generator[Ear, None, None]:
        # Enforce global CCW once so ear detection, diagonal tests, and final merge are consistent.
        if not titanic.is_ccw():
            titanic = Polygon(list(reversed(titanic)))
        # Ear clipping: while polygon has more than 3 vertices, find and clip an ear.
        while len(titanic) > 3:
            n: int = len(titanic)
            found: bool = False
            for j in range(n):

                # Only clip if we would leave at least 3 vertices (the last 3 are the final triangle).
                left: Point = titanic[j - 1]
                center: Point = titanic[j]
                right: Point = titanic[j + 1]

                # Check if the triangle is a valid ear.
                walk: Walk = Walk(start=left, center=center, end=right)
                if walk.is_collinear():
                    continue
                walk = walk if walk.is_ccw() else ~walk
                if not walk.is_ccw():
                    raise EarClippingFailureError(f"Triangle is not CCW: {walk}. " f"The polygon is: {titanic}.")

                # Check if the diagonal is inside the polygon.
                diagonal: Segment = left.to(right)
                if not titanic.contains(diagonal, inclusive=True):
                    continue

                # Check if the triangle contains any other vertices.
                triangle: Polygon = Polygon([left, center, right])
                excluded = ((j - 1) % n, j, (j + 1) % n)
                if any(triangle.contains(titanic[k], inclusive=False) for k in range(n) if k not in excluded):
                    continue

                # Add the ear to the table.
                ear = Ear([left, center, right])
                ear.sort("ccw")
                yield ear

                # Safecheck against bugs.
                found = True

                # Remove ear tip from polygon by index (position), not by point value;
                # the same point may appear at other indices and must be kept.
                titanic = Polygon([titanic[i] for i in range(n) if i != j])
                break

            # Safecheck against bugs.
            if not found:
                raise EarClippingFailureError(f"Iteration completed but no ear found for: {titanic}. ")

        # The remainder should contain exactly 3 vertices.
        if len(titanic) != 3:
            raise EarClippingFailureError(f"Expected 3 vertices or less; got {len(titanic)}." f"The polygon is: {titanic}.")

        # Add final triangle as last ear (ccw or reversed if cw).
        path: Walk = Walk(start=titanic[0], center=titanic[1], end=titanic[2])
        if path.is_collinear():
            raise EarClippingFailureError(f"Final triangle is collinear: {path}. " f"The polygon is: {titanic}.")
        ear = Ear([titanic[0], titanic[1], titanic[2]])
        ear.sort("ccw")
        yield ear

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.gallery = ArtGallery.unserialize(self.job.stdout)

        # Ear clipping: while polygon has more than 3 vertices, find and clip an ear.
        # clip() uses self.gallery.obstacles to reject ears that overlap a hole.
        ears: Table[Ear] = Table()
        for ear in self.clip(Polygon(list(self.gallery.stitched))):
            ears.add(ear)

        # There must be n - 2 ears (one per triangle in the triangulation).
        # NOTE: This is not true for polygons with repeated vertices.
        # if len(ears) != len(gallery.stitched) - 2:
        #     raise EarClippingFailureError(
        #         f"Expected {len(gallery.stitched) - 2} ears; got {len(ears)}. "
        #         f"The polygon is: {gallery.stitched}. "
        #         f"The ears are: {ears}. "
        #     )

        logger.info("EarClippingStep.run() | job.id=%s ears=%s", self.job.id, len(ears))
        return {"ears": ears.serialize()}


class ConvexComponentOptimizationStep(SequenceStep):
    """
    Convex component optimization step. Reads ears from job.stdout (from ear clipping step).
    Merges adjacent convex components; returns convex_components as Table.serialize().
    Ear.unserialize() raises if ears data is missing or invalid.

    Complexity: O(n^3), n = number of ears (triangles), on the order of stitched vertices.
    """

    def build_adjacency_table(self, table: Table[ConvexComponent]) -> Table[Bag[ConvexComponent, Identifier]]:
        """
        Build Table[Bag[ConvexComponent, Identifier]] from Table[ConvexComponent]: index by edge,
        then for each component create a bag and add ids of components sharing an edge.
        Serializes as dict mapping component id -> list of adjacent component ids.
        """
        components_by_edge: defaultdict[Segment, list[ConvexComponent]] = defaultdict(list)
        for component in table:
            for edge in component.edges:
                components_by_edge[edge].append(component)
        result: Table[Bag[ConvexComponent, Identifier]] = Table()
        for component in table:
            bag: Bag[ConvexComponent, Identifier] = Bag(component)
            for edge in component.edges:
                for other in components_by_edge[edge]:
                    if other is not component:
                        bag += other.id
            result.add(bag)
        return result

    def run(self, **kwargs: Any) -> dict[str, Any]:
        gallery: ArtGallery = ArtGallery.unserialize(self.job.stdout)
        ears: Table[Ear] = gallery.ears
        components_table: Table[ConvexComponent] = Table.unserialize([ConvexComponent(ear) for ear in ears])
        adjacency_table: Table[Bag[ConvexComponent, Identifier]] = self.build_adjacency_table(components_table)
        logger.info("ConvexComponentOptimizationStep.run() | job.id=%s components=%s", self.job.id, len(components_table))

        # Merge adjacent pairs by largest area until no merge possible.
        while True:
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
                break

            # Merge the best pair, and update the tables.
            components_table -= best_pair[0]
            components_table -= best_pair[1]
            components_table += best_merge
            adjacency_table = self.build_adjacency_table(components_table)

        logger.info("ConvexComponentOptimizationStep.run() | job.id=%s components_after_merges=%s", self.job.id, len(components_table))
        return {"convex_components": components_table.serialize(), "adjacency": adjacency_table.serialize()}


class GuardPlacementStep(SequenceStep):
    """
    Guard placement step. Reads stitched, convex_components and adjacency from job.stdout.
    Boundary and obstacles come from stdout (merged from validation).

    Algorithm (same greedy logic with exploration heuristic for performance):
    1. Remaining state: all convex components and all stitched points (vertices to cover).
    2. Sort remaining components by size (signed area, largest first).
    3. Pick the largest component; its vertices are the guard candidates.
    4. Score each candidate via explore(guard): returns a Bag of points visible from that guard.
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

    def explore(self, guard: Point) -> Bag[Point, Point]:
        """
        Return a Bag(guard) of points visible from guard. Uses component_id_by_point to find
        all components the guard belongs to; hydrates visibility_by_segment and the visibility
        bag with all points of those components. Then expands via adjacent components; only
        adds adjacent-of-adjacent to explorable when the current component yielded at least
        one visible point.
        """
        visibility: Bag[Point, Point] = Bag(guard)

        if hash(guard) not in self.component_id_by_point:
            raise GuardNotInComponentIdByPointError("Guard not in component_id_by_point; invalid state (prepare() not run or guard not a vertex).")

        # Record the components that are already visible due to being a vertex of the guard's component.
        explored: set[Identifier] = set(self.component_id_by_point[guard].items)
        explorable: set[Identifier] = {
            adj_id for component_id in explored for adj_id in self.gallery.adjacency[self.gallery.convex_components[component_id]].items
        }

        # Hydrate visibility and cache with all points of every component the guard belongs to.
        for component_id in explored:
            component: ConvexComponent = self.gallery.convex_components[component_id]
            for point in component:
                segment: Segment = guard.to(point)
                self.visibility_by_segment[segment] = True
                visibility += point

        # Continue exploring explorable components until no more are available.
        while explorable - explored:

            # Find the adjacent component to explore.
            adjacent_id: Identifier = (explorable - explored).pop()
            adjacent: ConvexComponent = self.gallery.convex_components[adjacent_id]

            # Mark the component as explored.
            explored.add(adjacent_id)

            # Check if that adjacent component is visible.
            visible = False
            for point in adjacent:
                if self.sees(guard, point):
                    visibility += point
                    visible = True

            # If the component is visible, explore its adjacent components.
            if visible:
                explorable.update(self.gallery.adjacency[adjacent].items)

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

        # Check if the segment is inside the boundary.
        if not self.gallery.boundary.contains(segment, inclusive=True):
            self.visibility_by_segment[segment] = False
            return False

        # Reject if the segment crosses any boundary edge in the interior (not at endpoints).
        # This catches visibility lines that connect two boundary points but pass outside the gallery,
        # e.g. from a point on edge (8,2)-(10,10) to (7,10) crossing that same edge.
        for edge in self.gallery.boundary.edges:

            if edge.connects(segment):
                continue

            if segment.intersects(edge, inclusive=True):
                self.visibility_by_segment[segment] = False
                return False

        # Check if the segment intersects any obstacles (must not cross an obstacle edge in the interior).
        for obstacle in self.gallery.obstacles:

            # Exit early: segment is inside the obstacle.
            if obstacle.contains(segment.midpoint, inclusive=False):
                self.visibility_by_segment[segment] = False
                return False

            # Check if the segment intersects any obstacle edge (must not cross an obstacle edge in the interior).
            for edge in obstacle.edges:
                if edge.connects(segment):
                    continue
                if segment.intersects(edge, inclusive=False):
                    self.visibility_by_segment[segment] = False
                    return False

        # The segment is visible if no checks failed.
        self.visibility_by_segment[segment] = True
        return True

    def measure(self, convex_component: ConvexComponent) -> Decimal:
        """Return the signed area of the component, using instance cache signed_area_by_component to avoid recomputation."""
        if convex_component not in self.signed_area_by_component:
            self.signed_area_by_component[convex_component] = convex_component.signed_area
        return self.signed_area_by_component[convex_component]

    def prepare(self) -> None:
        """
        Hydrate self.component_id_by_point: for each convex component and each point in it,
        map the point to that component's id. Points on shared edges appear in multiple components.
        """
        self.component_id_by_point = Table()
        for component in self.gallery.convex_components:
            for point in component:
                key: int = hash(point)
                if key not in self.component_id_by_point:
                    self.component_id_by_point.add(Bag(point))
                bag = self.component_id_by_point[key]
                bag += component.id

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.gallery = ArtGallery.unserialize(self.job.stdout)
        self.visibility_by_segment: dict[Segment, bool] = {}
        self.signed_area_by_component: dict[ConvexComponent, Decimal] = {}
        self.component_id_by_point: Table[Bag[Point, Identifier]] = Table()

        self.prepare()

        remaining_points: set[Point] = set(self.gallery.stitched)
        remaining_components: set[ConvexComponent] = set(self.gallery.convex_components)
        logger.info("GuardPlacementStep.run() | job.id=%s points=%s components=%s", self.job.id, len(remaining_points), len(remaining_components))

        # Run until all points are covered.
        while remaining_points:

            # Safecheck against bugs.
            if not remaining_components:
                raise GuardCoverageFailureError("Failed to cover all points; no remaining convex components.")

            # Choose the guard (from any remaining component) that covers the most remaining points.
            best_guard: Point | None = None
            best_count: int = -1
            best_visibility: Bag[Point, Point] | None = None
            best_component: ConvexComponent | None = None
            for component in remaining_components:
                for guard in component:
                    bag: Bag[Point, Point] = self.explore(guard)
                    count: int = sum(1 for point in remaining_points if point in bag)
                    if count > best_count:
                        best_count = count
                        best_guard = guard
                        best_visibility = bag
                        best_component = component

            # Safecheck against bugs.
            if best_guard is None or best_count == 0 or best_visibility is None or best_component is None:
                raise GuardCoverageFailureError("Failed to find a guard that covers any remaining points.")
            if best_guard in self.gallery.guards:
                raise GuardCoverageFailureError("Best guard is already in the gallery.")

            # Add the best guard and its visibility to the gallery.
            self.gallery.guards += best_guard
            self.gallery.visibility += best_visibility

            # Remove the component and the points from the remaining sets.
            remaining_points -= set(best_visibility.items)
            remaining_components -= {best_component}

            # Remove any component fully covered by best_guard using best_visibility (avoids redundant sees() calls).
            for comp in list(remaining_components):
                if all(point in best_visibility for point in comp):
                    remaining_components -= {comp}

            logger.info("GuardPlacementStep.run() | job.id=%s points_remaining=%s", self.job.id, len(remaining_points))

        logger.info("GuardPlacementStep.run() | job.id=%s guards=%s", self.job.id, len(self.gallery.guards))
        return {
            "guards": self.gallery.guards.serialize(),
            "visibility": self.gallery.visibility.serialize(),
        }
