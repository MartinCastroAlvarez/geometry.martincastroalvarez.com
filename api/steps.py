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
from typing import Type

from attributes import Identifier
from attributes import Signature
from attributes import Work
from enums import Status
from enums import StepName
from exceptions import BridgeFailureError
from exceptions import ConvexComponentNotSimpleError
from exceptions import ConvexComponentOptimizationFailureError
from exceptions import EarClippingFailureError
from exceptions import NoMoreConvexComponentsMergeError
from exceptions import GuardCoverageFailureError
from exceptions import GuardNotInComponentIdByPointError
from exceptions import NoMoreEarsError
from exceptions import OnlyMidpointsRemainingError
from exceptions import PolygonNotSimpleError
from exceptions import PolygonsDoNotShareEdgeError
from exceptions import StepNotHandledError
from exceptions import StitchWinnerSubsequenceError
from exceptions import SuspendedStepError
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
from settings import CONVEX_COMPONENT_OPTIMIZATION_MAX_WORK
from settings import EAR_CLIPPING_MAX_WORK
from settings import GUARD_PLACEMENT_MAX_WORK
from settings import STITCH_BUCKET_SIZE
from settings import STITCHING_MAX_WORK
from states import ArtGalleryStepState
from states import ConvexComponentOptimizationStepState
from states import EarClippingStepState
from states import GuardPlacementStepState
from states import State
from states import StitchingStepState
from states import ValidationPolygonStepState
from structs import Collection
from structs import Table

logger = logging.getLogger(__name__)


def work(max_work: int):
    """
    Decorator for step instance methods: increments self.work by 1 each call;
    if self.work > max_work, calls self.suspend() before invoking the method.
    Use a value from settings (e.g. STITCHING_MAX_WORK, GUARD_PLACEMENT_MAX_WORK).
    """

    def decorator(f):
        def wrapper(self, *args, **kwargs):
            self.work = self.work + 1
            if self.work > max_work:
                self.suspend()
            return f(self, *args, **kwargs)

        return wrapper

    return decorator


class Step(ABC):
    """
    Abstract pipeline step. Receives a Job and user; run() returns a dict
    merged into job.stdout. Idempotent: given the same job and inputs, running
    multiple times must produce the same outcome and must not duplicate side effects.
    All steps have two main attributes: self.gallery and self.state.
    """

    STATE_CLASS: Type[State] = State

    def __init__(self, job: Job, user: User, state: dict) -> None:
        self.job: Job = job
        self.user: User = user
        self.work: Work = Work(0)
        self.state: State = self.STATE_CLASS.unserialize(state)
        self._state_was_empty: bool = state == {}

    @abstractmethod
    def init(self) -> None:
        """Initialize step state when starting fresh (state was empty). Subclasses must implement."""
        raise NotImplementedError

    @cached_property
    def repository(self) -> JobsRepository:
        """JobsRepository for the step's user. Cached for the lifetime of the step instance."""
        return JobsRepository(user=self.user)

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

    def suspend(self) -> None:
        """
        Raise SuspendedStepError with current step state so the task handler can requeue().
        The exception carries self.state.serialize() so tasks.py dumps the state to the repository.
        """
        raise SuspendedStepError("Step suspended", state=self.state.serialize())

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

    STATE_CLASS: Type[State] = ArtGalleryStepState

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gallery: ArtGallery = ArtGallery.unserialize(self.job.stdin)

    def init(self) -> None:
        pass

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

    STATE_CLASS: Type[State] = ValidationPolygonStepState

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gallery: ArtGallery = ArtGallery.unserialize(self.job.stdin)

    def init(self) -> None:
        pass

    def validate_simplicity(self) -> None:
        """
        Ensure boundary and every obstacle are simple (degree 2, no self-intersection).
        Required so later steps (ear clipping, stitching) operate on well-defined polygons.
        """
        if not self.gallery.boundary.is_simple():
            raise PolygonNotSimpleError("Boundary polygon is not simple.")
        if any(not obstacle.is_simple() for obstacle in self.gallery.obstacles):
            raise PolygonNotSimpleError("Obstacle polygon is not simple.")

    def validate_orientation(self) -> None:
        """
        Ensure boundary is CCW (outer ring) and every obstacle is CW (hole).
        Convention required for containment tests and stitching (bridge/merge logic).
        """
        self.gallery.boundary.sort("ccw")
        for obstacle in self.gallery.obstacles:
            obstacle.sort("cw")

    def validate_containment(self) -> None:
        """
        Ensure every obstacle vertex lies strictly inside the boundary.
        Obstacles must be holes fully enclosed by the outer polygon for valid stitching.
        """
        if any(not all(self.gallery.boundary.contains(point, inclusive=False) for point in obstacle) for obstacle in self.gallery.obstacles):
            raise ValidationObstacleNotContainedError(f"Obstacle is not strictly inside the boundary ({self.gallery.boundary}).")

    def validate_intersections(self) -> None:
        """
        Ensure no invalid contact: obstacle edges must not cross/touch boundary edges
        (except at shared vertices), no obstacle vertex on a boundary edge, and no
        two obstacles may intersect or touch. Prevents ambiguous topology for bridging.
        """
        if any(
            _segments_intersect(edge, boundary_edge, inclusive=True) and not _segments_share_endpoint(edge, boundary_edge)
            for obstacle in self.gallery.obstacles
            for edge in obstacle.edges
            for boundary_edge in self.gallery.boundary.edges
        ):
            raise PolygonNotSimpleError("Obstacle edge intersects or touches boundary.")
        if any(
            boundary_edge.contains(point, inclusive=True)
            for obstacle in self.gallery.obstacles
            for point in obstacle
            for boundary_edge in self.gallery.boundary.edges
        ):
            raise PolygonNotSimpleError("Obstacle has a vertex on the boundary.")
        if any(
            obstacle.intersects(other, inclusive=True) for obstacle in self.gallery.obstacles for other in self.gallery.obstacles if obstacle != other
        ):
            raise PolygonNotSimpleError("Obstacles intersect or touch.")

    def run(self, **kwargs: Any) -> dict[str, Any]:
        self.validate_simplicity()
        self.validate_orientation()
        self.validate_containment()
        self.validate_intersections()
        logger.info("ValidationPolygonStep.run() | job.id=%s obstacles=%s", self.job.id, len(self.gallery.obstacles))
        return {
            "boundary": self.gallery.boundary.serialize(),
            "obstacles": [obstacle.serialize() for obstacle in self.gallery.obstacles],
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

    STATE_CLASS: Type[State] = StitchingStepState

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gallery: ArtGallery = ArtGallery.unserialize(self.job.stdout)
        if self._state_was_empty:
            self.init()
        # Gallery is read-only; state holds points, stitches, remaining_obstacles

    def init(self) -> None:
        self.state.points = Polygon(list(self.gallery.boundary))
        self.state.stitches = []
        self.state.remaining_obstacles = self.sort()

    def sort(self) -> list[Polygon]:
        """Return obstacles sorted by rightmost vertex (x, y) descending for bridge order."""
        obstacles = list(self.gallery.obstacles)
        obstacles.sort(key=lambda obstacle: (obstacle.rightmost.x, obstacle.rightmost.y), reverse=True)
        return obstacles

    @work(STITCHING_MAX_WORK)
    def bridge(self, obstacle: Polygon) -> None:
        """Find a valid bridge from state.points to obstacle, merge, and update state.points and state.stitches."""
        obstacle.sort("cw")
        bridge: Segment | None = None
        anchor: Point | None = None
        stitched: Polygon = self.state.points
        obstacles: list[Polygon] = self.state.remaining_obstacles

        # Find the valid bridge from the obstacle to the stitched polygon.
        # After lots of testing, there is no real benefit in finding the shortest bridge.
        # Any bridge that is valid will do.
        i: int = 0
        for anchor in obstacle:
            bridge = None
            for candidate in stitched << stitched.rightmost:
                if candidate == anchor:
                    continue
                segment: Segment = candidate.to(anchor)
                if not self.gallery.boundary.contains(segment, inclusive=True):
                    continue
                if any(other.intersects(segment, inclusive=False) for other in obstacles if other is not obstacle):
                    continue
                if any(segment.crosses(edge) for edge in obstacle.edges):
                    continue
                if any(
                    Walk(start=edge[0], center=edge[1], end=segment[0]).is_collinear()
                    and Walk(start=edge[0], center=edge[1], end=segment[1]).is_collinear()
                    for edge in self.gallery.boundary.edges
                    if not _segments_share_endpoint(edge, segment)
                ):
                    continue
                if any(segment.crosses(edge) for edge in stitched.edges):
                    continue
                if i >= STITCH_BUCKET_SIZE:
                    break
                i += 1
                if bridge is None or segment.size < bridge.size:
                    bridge = segment
            if bridge is not None:
                break

        # Validate that the bridge is valid.
        if bridge is None or anchor is None:
            raise BridgeFailureError(f"No valid bridge found for obstacle: {obstacle}")

        # Define the vertex of the bridge.
        vertex: Point = bridge[0]

        # Validate that the bridge is not a subsequence of the boundary or the obstacle.
        if bridge in stitched:
            raise StitchWinnerSubsequenceError("Winner is a subsequence of boundary points; cannot stitch")
        if bridge in obstacle:
            raise StitchWinnerSubsequenceError("Winner is a subsequence of obstacle; cannot stitch")

        # Update state.points and state.stitches.
        left: Polygon = Polygon(list(stitched))
        right: Polygon = Polygon(list(obstacle))

        # Sort polygons so that they can be merged.
        left.sort("ccw")
        right.sort("cw")

        # Rotate polygons so that they can be merged.
        left = left >> vertex
        right = right << anchor

        # Validate that the polygons can be merged correctly.
        assert right[0] == anchor, f"Right polygon does not start with anchor: {right}"
        assert left[-1] == vertex, f"Left polygon does not end with vertex: {left}"

        # Merge the polygons.
        merged: list[Point] = list(left) + list(right) + [anchor, vertex]

        # Update the state.
        self.state.points = Polygon(merged)
        self.state.stitches.append(bridge)

    def run(self, **kwargs: Any) -> dict[str, Any]:
        logger.info(
            "StitchingStep.run() | job.id=%s obstacles=%s boundary_points=%s",
            self.job.id,
            len(self.state.remaining_obstacles),
            len(self.gallery.boundary),
        )
        while self.state.remaining_obstacles:
            obstacle = self.state.remaining_obstacles.pop(0)
            self.bridge(obstacle)

        if len(self.state.points) > 0:
            assert self.state.points.is_ccw(), f"Stitched polygon is not CCW: {self.state.points}"
        logger.info(
            "StitchingStep.run() | job.id=%s stitched_points=%s bridge_edges=%s",
            self.job.id,
            len(self.state.points),
            len(self.state.stitches),
        )
        return {"stitched": self.state.points.serialize(), "stitches": [s.serialize() for s in self.state.stitches]}


class EarClippingStep(SequenceStep):
    """
    Ear clipping step. Reads stitched polygon from job.stdout (from stitching step).
    Runs ear clipping only; returns ears as Table.serialize().
    Polygon.unserialize() raises if stitched is missing or invalid.
    Rejects any ear whose segments (vertex–vertex or vertex–edge-midpoint) cross an obstacle,
    so that downstream steps can assume components are obstacle-safe.

    Complexity: O(n^3), n = number of vertices of the stitched polygon.
    """

    STATE_CLASS: Type[State] = EarClippingStepState

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gallery: ArtGallery = ArtGallery.unserialize(self.job.stdout)
        if self._state_was_empty:
            self.init()
        # Gallery is read-only; state holds titanic and ears

    def init(self) -> None:
        self.state.titanic = Polygon(list(self.gallery.stitched))
        # self.state.titanic.sort("ccw")  # This breaks everything.
        self.state.ears = Table()

    @work(EAR_CLIPPING_MAX_WORK)
    def clip(self) -> Ear:
        """
        Find and clip the next ear from state.titanic; update state.ears and state.titanic.
        Returns the ear, or raises NoMoreEarsError when done (≤3 vertices left).
        """
        n: int = len(self.state.titanic)

        # Polygon reduced to ≤3 vertices: add final triangle as last ear if exactly 3, then signal done.
        if n <= 3:
            if n == 3:
                path: Walk = Walk(start=self.state.titanic[0], center=self.state.titanic[1], end=self.state.titanic[2])
                if not path.is_collinear():
                    ear = Ear([self.state.titanic[0], self.state.titanic[1], self.state.titanic[2]])
                    ear.sort("ccw")
                    self.state.ears.add(ear)
            raise NoMoreEarsError("No more ears to clip")

        # Ear clipping: find one valid ear (only clip if we would leave at least 3 vertices).
        for j in range(n):
            # Check if the triangle (j-1, j, j+1) is a valid ear.
            walk: Walk = Walk(start=self.state.titanic[j - 1], center=self.state.titanic[j], end=self.state.titanic[j + 1])

            # CW ears are not valid because they contain empty space.
            if walk.is_collinear() or walk.is_cw():
                continue

            # Build the ear from the CCW walk.
            ear = Ear(list(walk))

            # The ear must be fully inside the boundary.
            if not self.state.titanic.contains(ear.diagonal, inclusive=True):
                continue

            # The ear must not contain any other vertices.
            if any(
                ear.contains(self.state.titanic[k], inclusive=False)
                for k in range(n)
                # Do not compare about the points of the ear itself.
                if k not in ((j - 1) % n, j, (j + 1) % n)
                # Do not compare with cycles that resulted from stitching.
                and self.state.titanic[k] not in {walk.start, walk.center, walk.end}
            ):
                continue

            # Add the ear to the table and remove ear tip from polygon by index (position), not by point value;
            # the same point may appear at other indices and must be kept.
            self.state.ears.add(ear)
            self.state.titanic.pop(j)
            return ear

        raise EarClippingFailureError(f"No valid ear found for polygon: {self.state.titanic}")

    def run(self, **kwargs: Any) -> dict[str, Any]:
        while True:
            try:
                self.clip()
            except NoMoreEarsError:
                break

        if not self.state.ears:
            raise EarClippingFailureError("No ears found for polygon")
        logger.info("EarClippingStep.run() | job.id=%s ears=%s", self.job.id, len(self.state.ears))
        return {"ears": self.state.ears.serialize()}


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

    STATE_CLASS: Type[State] = ConvexComponentOptimizationStepState

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gallery: ArtGallery = ArtGallery.unserialize(self.job.stdout)
        if self._state_was_empty:
            self.init()

    def init(self) -> None:
        """Build initial convex_components from ears and adjacency table; store both in state."""
        ears: Table[Ear] = self.gallery.ears
        self.state.convex_components = Table.unserialize([ConvexComponent(ear) for ear in ears])
        self.state.adjacency = self.build_adjacency_table(self.state.convex_components)

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

    @work(CONVEX_COMPONENT_OPTIMIZATION_MAX_WORK)
    def merge(self) -> None:
        """
        Perform one merge: find the best adjacent pair by area, merge them, and update state.
        Raises NoMoreConvexComponentsMergeError when no valid merge is possible.
        """
        best_area: Decimal | None = None
        best_merge: ConvexComponent | None = None
        best_pair: tuple[ConvexComponent, ConvexComponent] | None = None
        for component in self.state.convex_components:
            for adjacent_id in self.state.adjacency[component]:
                adjacent: ConvexComponent = self.state.convex_components[adjacent_id]
                try:
                    merged: ConvexComponent = component + adjacent
                except (ValidationError, ConvexComponentNotSimpleError, PolygonsDoNotShareEdgeError):
                    continue
                if best_area is None or abs(merged.signed_area) > best_area:
                    best_area = abs(merged.signed_area)
                    best_merge = merged
                    best_pair = (component, adjacent)

        if best_pair is None or best_merge is None:
            raise NoMoreConvexComponentsMergeError("No more convex component merges possible")

        logger.debug(
            "ConvexComponentOptimizationStep.merge() | job.id=%s id_a=%s id_b=%s merged_area=%s components_before=%s",
            self.job.id,
            best_pair[0].id,
            best_pair[1].id,
            best_area,
            len(self.state.convex_components),
        )
        self.state.convex_components -= best_pair[0]
        self.state.convex_components -= best_pair[1]
        self.state.convex_components += best_merge
        self.state.adjacency = self.build_adjacency_table(self.state.convex_components)

    def run(self, **kwargs: Any) -> dict[str, Any]:
        logger.info("ConvexComponentOptimizationStep.run() | job.id=%s components=%s", self.job.id, len(self.state.convex_components))
        while True:
            try:
                self.merge()
            except NoMoreConvexComponentsMergeError:
                break
        logger.info("ConvexComponentOptimizationStep.run() | job.id=%s components_after_merges=%s", self.job.id, len(self.state.convex_components))
        if len(self.state.convex_components) == 0:
            raise ConvexComponentOptimizationFailureError("No convex components found")
        return {"convex_components": self.state.convex_components.serialize(), "adjacency": self.state.adjacency.serialize()}


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

    STATE_CLASS: Type[State] = GuardPlacementStepState

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.gallery: ArtGallery = ArtGallery.unserialize(self.job.stdout)
        if self._state_was_empty:
            self.prepare()
            self.state.remaining_component_ids = {c.id for c in self.gallery.convex_components}

    def init(self) -> None:
        pass

    def measure(self, convex_component: ConvexComponent) -> int:
        """Return the number of points (vertices and edge midpoints) of the component that are not in remaining_points."""
        points: list[Point] = list(convex_component) + [edge.midpoint for edge in convex_component.edges]
        return len([p for p in points if p not in self.state.remaining_points])

    def explore(self, guard: Point) -> Collection[Point, Point]:
        """
        Return a Collection(guard) of points visible from guard. Uses component_id_by_point to find
        all components the guard belongs to; hydrates visibility_by_segment and the visibility
        collection with all points of those components. Then expands via adjacent components; only
        adds adjacent-of-adjacent to explorable when the current component yielded at least
        one visible point.
        """
        visibility: Collection[Point, Point] = Collection(guard)

        if hash(guard) not in self.state.component_id_by_point:
            raise GuardNotInComponentIdByPointError("Guard not in component_id_by_point; invalid state (prepare() not run or guard not a vertex).")

        # Record the components that are already visible due to being a vertex of the guard's component.
        explored: set[Identifier] = set(self.state.component_id_by_point[hash(guard)])
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

    @work(GUARD_PLACEMENT_MAX_WORK)
    def sees(self, guard: Point, target: Point) -> bool:
        """
        True if target is visible from guard in the art gallery. Caches by segment in visibility_by_segment.
        Only uncached visibility checks count as work; guard==target or cache hit undo the decorator's increment.
        """
        if guard == target:
            self.work -= 1
            return True
        segment: Segment = guard.to(target)
        if segment in self.state.visibility_by_segment:
            self.work -= 1
            return self.state.visibility_by_segment[segment]

        # Segment must lie inside or on the boundary polygon.
        if not self.gallery.boundary.contains(segment, inclusive=True):
            self.state.visibility_by_segment[segment] = False
            return False

        for obstacle in self.gallery.obstacles:

            # No obstacle may contain the segment midpoint (strictly inside obstacle => blocked).
            if obstacle.intersects(segment.midpoint, inclusive=False):
                self.state.visibility_by_segment[segment] = False
                return False

            # No obstacle edge may properly cross the segment (line-of-sight cut).
            for edge in obstacle.edges:
                if segment.crosses(edge):
                    self.state.visibility_by_segment[segment] = False
                    return False
        self.state.visibility_by_segment[segment] = True
        return True

    def prepare(self) -> None:
        """
        Hydrate state from gallery (read-only). Set remaining_points and component maps;
        do not mutate gallery.
        """
        coverage: set[Point] = set(self.gallery.stitched) | {mp for c in self.gallery.convex_components for mp in c.midpoints}
        self.state.remaining_points = set(coverage)
        self.state.component_id_by_point = {}
        self.state.component_id_by_midpoint = defaultdict(set)
        for component in self.gallery.convex_components:
            for point in component:
                self.state.component_id_by_point.setdefault(hash(point), []).append(component.id)
            for midpoint in component.midpoints:
                self.state.component_id_by_midpoint[midpoint].add(component.id)

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
            guard: sum(1 for point in self.state.remaining_points if point in visibility_by_guard[guard]) for guard in candidates
        }
        key = lambda guard: (coverage_by_guard[guard], len(visibility_by_guard[guard]), hash(guard))
        sorted_candidates: list[Point] = sorted(candidates, key=key, reverse=True)
        return sorted_candidates[0], visibility_by_guard[sorted_candidates[0]]

    def analyze(self) -> None:
        """
        Build exclusivity table in state: for each guard, points visible only by that guard.
        Reads state.guards and state.visibility; writes state.exclusivity.
        """
        self.state.exclusivity = Table()
        for guard in list(self.state.guards):
            visibility: Collection[Point, Point] = self.state.visibility[guard]
            other_points: set[Point] = {
                point for other in self.state.guards.values() if other != guard for point in self.state.visibility[other].items
            }
            exclusive: set[Point] = set(visibility.items) - other_points
            if not exclusive:
                self.state.guards -= guard
                self.state.visibility -= guard
                continue
            exclusivity: Collection[Point, Point] = Collection(guard)
            for point in exclusive:
                exclusivity += point
            self.state.exclusivity += exclusivity

    def propose(self, max_candidates: int = 10) -> list[Point]:
        """
        Return the candidates to compete.
        It reduces the number of explore() calls later in self.compete().

        Returns:
            list[Point]: The candidates to compete.
        """
        if not self.state.remaining_component_ids:
            raise OnlyMidpointsRemainingError("Only midpoints remain.")
        key = lambda c: (self.measure(c), len(c), c.id)
        sorted_components: list[ConvexComponent] = sorted(
            [self.gallery.convex_components[cid] for cid in self.state.remaining_component_ids], key=key
        )
        largest_component: ConvexComponent = sorted_components[0]
        return list(largest_component)[:max_candidates]

    def run(self, **kwargs: Any) -> dict[str, Any]:
        # Run until all points are covered.
        while self.state.remaining_points:
            logger.debug(
                "GuardPlacementStep.run() | job.id=%s points_remaining=%s components_remaining=%s",
                self.job.id,
                len(self.state.remaining_points),
                len(self.state.remaining_component_ids),
            )

            # Find the best candidates to compete.
            # Sometimes only midpoints remain, even though they are not valid candidates.
            # We need to propose candidates that are in the same components as the remaining points.
            try:
                candidates: list[Point] = self.propose()
            except OnlyMidpointsRemainingError:
                candidates_list: list[Point] = [
                    self.gallery.convex_components[component_id][0]
                    for midpoint in self.state.remaining_points
                    for component_id in self.state.component_id_by_midpoint[midpoint]
                ]
                candidates = list(candidates_list)
                assert candidates, f"Candidates are all monsters: f{self.state.remaining_points}"

            # Add the best guard and its visibility to state (gallery is read-only until completion).
            best_guard, best_visibility = self.compete(candidates)
            self.state.guards += best_guard
            self.state.visibility += best_visibility
            assert len(best_visibility) > 0, f"GuardPlacementStep.run() | job.id={self.job.id} best_visibility={best_visibility}"
            self.state.remaining_points -= set(best_visibility)

            # Remove any component fully covered by best_guard using best_visibility (avoids redundant sees() calls).
            for cid in list(self.state.remaining_component_ids):
                component: ConvexComponent = self.gallery.convex_components[cid]
                if any(point in self.state.remaining_points for point in component):
                    continue
                if any(midpoint in self.state.remaining_points for midpoint in component.midpoints):
                    continue
                self.state.remaining_component_ids -= {cid}
            logger.info("GuardPlacementStep.run() | job.id=%s points_remaining=%s", self.job.id, len(self.state.remaining_points))

        logger.info("GuardPlacementStep.run() | job.id=%s guards=%s", self.job.id, len(self.state.guards))
        if len(self.state.guards) == 0:
            raise GuardCoverageFailureError("No guards placed")
        assert not self.state.remaining_component_ids, "Remaining components should be empty."
        assert not self.state.remaining_points, "Remaining points should be empty."

        self.analyze()

        coverage: set[Point] = set(self.gallery.stitched) | {mp for c in self.gallery.convex_components for mp in c.midpoints}
        return {
            "guards": self.state.guards.serialize(),
            "visibility": {str(hash(bag.key)): [p.serialize() for p in bag.items] for bag in self.state.visibility},
            "exclusivity": {str(hash(bag.key)): [p.serialize() for p in bag.items] for bag in self.state.exclusivity},
            "coverage": [p.serialize() for p in coverage],
        }
