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
from enums import Status
from enums import StepName
from exceptions import BridgeFailureError
from exceptions import EarClippingFailureError
from exceptions import GuardCoverageFailureError
from exceptions import PolygonNotSimpleError
from exceptions import PolygonsDoNotShareEdgeError
from exceptions import StepNotHandledError
from exceptions import StitchWinnerSubsequenceError
from exceptions import ValidationBoundaryNotCCWError
from exceptions import ValidationError
from exceptions import ValidationObstacleNotCWError
from geometry import Point
from geometry import Polygon
from geometry.convex import ConvexComponent
from geometry.ear import Ear
from geometry.segment import Segment
from geometry.walk import Walk
from models import Job
from models import User
from repositories import JobsRepository
from settings import STITCH_BUCKET_SIZE

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
        return {
            "boundary": self.job.stdin.get("boundary"),
            "obstacles": self.job.stdin.get("obstacles"),
        }


class ValidationPolygonStep(SequenceStep):
    """
    Validates boundary and obstacles using api/geometry (same logic as lab ArtGallery.validate()).
    Parses boundary and obstacles via Polygon.unserialize(); let it throw. On success returns step
    result and calls broadcast(). We do not catch Exception; let failures raise so StartTask handles them.
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
        if not self.boundary.is_ccw():
            raise ValidationBoundaryNotCCWError()
        if any(not obstacle.is_cw() for obstacle in self.obstacles):
            raise ValidationObstacleNotCWError()

    def validate_containment(self) -> None:
        """
        Ensure every obstacle vertex lies strictly inside the boundary.
        Obstacles must be holes fully enclosed by the outer polygon for valid stitching.
        """
        assert self.boundary is not None
        if any(not all(self.boundary.contains(point, inclusive=False) for point in obstacle) for obstacle in self.obstacles):
            raise PolygonNotSimpleError(f"Obstacle is not strictly inside the boundary ({self.boundary}).")

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
        self.boundary = Polygon.unserialize(self.job.stdin.get("boundary"))
        self.obstacles = [Polygon.unserialize(obstacle) for obstacle in (self.job.stdin.get("obstacles") or [])]
        self.validate_simplicity()
        self.validate_orientation()
        self.validate_containment()
        self.validate_intersections()
        return {}


class StitchingStep(SequenceStep):
    """
    Stitching step: merges boundary and obstacles into a single polygon (stitched)
    by sorting obstacles by rightmost vertex and bridging each to the current outer
    polygon. Same logic as lab ArtGallery.points. Idempotent: same job and inputs
    yield the same stitched polygon. Emits "stitched" (serialized Polygon) and
    "stitches" (list of serialized bridge Segment) in stdout.

    Performance optimization (see docs 3 BACKEND.md and 12 PROTOTYPE.md): we iterate
    polygon points starting from the rightmost (using Sequence shift from structs.py;
    one O(n) rotation per obstacle, cheap). We keep a bucket of the shortest
    STITCH_BUCKET_SIZE valid bridges; once the bucket is full we pick the smallest
    by size and stop, avoiding full O(n) checks when good short bridges exist.
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
        # Parse boundary and obstacles from job stdin (Polygon.unserialize may raise).
        self.boundary = Polygon.unserialize(self.job.stdin.get("boundary"))
        self.obstacles = [Polygon.unserialize(obstacle) for obstacle in (self.job.stdin.get("obstacles") or [])]

        # No obstacles: stitched result is the boundary; no bridge edges added.
        if not self.obstacles:
            self.points = self.boundary
            return {"stitched": self.points.serialize(), "stitches": []}

        # Sort obstacles by rightmost vertex (desc) and init working polygon and its edges.
        self.sort()
        assert self.boundary is not None
        logger.info("Stitching %d obstacles to boundary (%d points).", len(self.obstacles), len(self.boundary))
        points: Polygon = Polygon(list(self.boundary))
        edges: list[Segment] = list(points.edges)
        stitches: list[Segment] = []

        for obstacle in self.obstacles:
            obstacle.sort("cw")
            anchors: list[Point] = sorted(
                list(obstacle),
                key=lambda point: (point.x, point.y),
                reverse=True,
            )
            bridge: Segment | None = None
            anchor: Point | None = None

            for anchor in anchors:
                bridge = None
                bucket: list[Segment] = []
                for candidate in points << points.rightmost:
                    if candidate == anchor:
                        continue
                    segment: Segment = candidate.to(anchor)
                    if not self.boundary.contains(segment, inclusive=True):
                        continue
                    if any(other.intersects(segment, inclusive=False) for other in self.obstacles):
                        continue
                    if any(
                        Walk(start=edge[0], center=edge[1], end=segment[0]).is_collinear()
                        and Walk(start=edge[0], center=edge[1], end=segment[1]).is_collinear()
                        for edge in self.boundary.edges
                        if not edge.connects(segment)
                    ):
                        continue
                    if any(edge.intersects(segment) for edge in edges if not edge.connects(segment)):
                        continue
                    bucket.append(segment)
                    bucket.sort(key=lambda s: s.size)
                    bucket = bucket[:STITCH_BUCKET_SIZE]
                    if len(bucket) >= STITCH_BUCKET_SIZE:
                        bridge = bucket[0]
                        break
                    if bridge is None or segment.size < bridge.size:
                        bridge = segment
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
        return {"stitched": self.points.serialize(), "stitches": [s.serialize() for s in stitches]}


class EarClippingStep(SequenceStep):
    """
    Ear clipping step. Idempotent: given the same job and inputs, running
    multiple times produces the same outcome. Recomputes stitched polygon from
    boundary and obstacles, then runs ear clipping (same logic as lab ArtGallery.ears).
    Returns ears as list of serialized Ear (each Ear is 3 points).
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        # Parse boundary and obstacles from job stdin.
        boundary: Polygon = Polygon.unserialize(self.job.stdin.get("boundary"))
        obstacles: list[Polygon] = [Polygon.unserialize(obstacle) for obstacle in (self.job.stdin.get("obstacles") or [])]
        points: Polygon
        if not obstacles:
            points = boundary
        else:
            # Sort obstacles by rightmost vertex (desc) and stitch each to the current polygon.
            obstacles = sorted(obstacles, key=lambda obstacle: (obstacle.rightmost.x, obstacle.rightmost.y), reverse=True)
            points = Polygon(list(boundary))
            edges: list[Segment] = list(points.edges)
            for obstacle in obstacles:
                obstacle.sort("cw")
                anchors: list[Point] = sorted(list(obstacle), key=lambda point: (point.x, point.y), reverse=True)
                bridge: Segment | None = None
                anchor: Point | None = None
                # Find shortest valid bridge from polygon to obstacle anchor (bucket of candidates).
                for anchor in anchors:
                    bridge = None
                    bucket: list[Segment] = []
                    for candidate in points << points.rightmost:
                        if candidate == anchor:
                            continue
                        segment: Segment = candidate.to(anchor)
                        if not boundary.contains(segment, inclusive=True):
                            continue
                        if any(other.intersects(segment, inclusive=False) for other in obstacles):
                            continue
                        if any(
                            Walk(start=edge[0], center=edge[1], end=segment[0]).is_collinear()
                            and Walk(start=edge[0], center=edge[1], end=segment[1]).is_collinear()
                            for edge in boundary.edges
                            if not edge.connects(segment)
                        ):
                            continue
                        if any(edge.intersects(segment) for edge in edges if not edge.connects(segment)):
                            continue
                        bucket.append(segment)
                        bucket.sort(key=lambda s: s.size)
                        bucket = bucket[:STITCH_BUCKET_SIZE]
                        if len(bucket) >= STITCH_BUCKET_SIZE:
                            bridge = bucket[0]
                            break
                        if bridge is None or segment.size < bridge.size:
                            bridge = segment
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
        # Ear clipping: while polygon has more than 3 vertices, find and clip an ear.
        ears: list[Ear] = []
        while len(points) > 3:
            titanic: Polygon = Polygon(list(points))
            n: int = len(points)
            found: int | None = None
            # Find first valid ear: convex turn, diagonal inside polygon, no other vertex inside triangle.
            for j in range(n):
                left_pt: Point = points[j - 1]
                center_pt: Point = points[j]
                right_pt: Point = points[(j + 1) % n]
                walk: Walk = Walk(start=left_pt, center=center_pt, end=right_pt)
                if walk.is_collinear():
                    continue
                if not walk.is_ccw():
                    continue
                diagonal: Segment = left_pt.to(right_pt)
                if not titanic.contains(diagonal, inclusive=True):
                    continue
                tri: Polygon = Polygon([left_pt, center_pt, right_pt])
                if any(tri.contains(points[k], inclusive=False) for k in range(n) if k not in ((j - 1) % n, j, (j + 1) % n)):
                    continue
                found = j
                ears.append(Ear([left_pt, center_pt, right_pt]))
                break
            if found is None:
                raise EarClippingFailureError(f"No ear found for: {points}")
            # Remove ear tip from polygon and continue.
            points = Polygon([points[i] for i in range(n) if i != found])
        # Add final triangle as last ear (ccw or reversed if cw).
        if len(points) == 3:
            path: Walk = Walk(start=points[0], center=points[1], end=points[2])
            if path.is_collinear():
                pass
            elif path.is_ccw():
                ears.append(Ear([points[0], points[1], points[2]]))
            else:
                ears.append(Ear([points[2], points[1], points[0]]))
        return {"ears": [ear.serialize() for ear in ears]}


class ConvexComponentOptimizationStep(SequenceStep):
    """
    Convex component optimization step. Idempotent: given the same job and
    inputs, running multiple times produces the same outcome. Recomputes
    stitch and ear clipping, then merges adjacent convex components (same
    logic as lab ArtGallery.convex_components). Returns convex_components
    as list of serialized ConvexComponent.
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        # Parse boundary and obstacles from job stdin.
        boundary: Polygon = Polygon.unserialize(self.job.stdin.get("boundary"))
        obstacles: list[Polygon] = [Polygon.unserialize(obstacle) for obstacle in (self.job.stdin.get("obstacles") or [])]
        points: Polygon
        if not obstacles:
            points = boundary
        else:
            # Sort obstacles by rightmost vertex (desc) and stitch each to the current polygon.
            obstacles = sorted(obstacles, key=lambda obstacle: (obstacle.rightmost.x, obstacle.rightmost.y), reverse=True)
            points = Polygon(list(boundary))
            edges: list[Segment] = list(points.edges)
            for obstacle in obstacles:
                obstacle.sort("cw")
                anchors: list[Point] = sorted(list(obstacle), key=lambda point: (point.x, point.y), reverse=True)
                bridge: Segment | None = None
                anchor: Point | None = None
                # Find shortest valid bridge from polygon to obstacle anchor (bucket of candidates).
                for anchor in anchors:
                    bridge = None
                    bucket: list[Segment] = []
                    for candidate in points << points.rightmost:
                        if candidate == anchor:
                            continue
                        segment: Segment = candidate.to(anchor)
                        if not boundary.contains(segment, inclusive=True):
                            continue
                        if any(other.intersects(segment, inclusive=False) for other in obstacles):
                            continue
                        if any(
                            Walk(start=edge[0], center=edge[1], end=segment[0]).is_collinear()
                            and Walk(start=edge[0], center=edge[1], end=segment[1]).is_collinear()
                            for edge in boundary.edges
                            if not edge.connects(segment)
                        ):
                            continue
                        if any(edge.intersects(segment) for edge in edges if not edge.connects(segment)):
                            continue
                        bucket.append(segment)
                        bucket.sort(key=lambda s: s.size)
                        bucket = bucket[:STITCH_BUCKET_SIZE]
                        if len(bucket) >= STITCH_BUCKET_SIZE:
                            bridge = bucket[0]
                            break
                        if bridge is None or segment.size < bridge.size:
                            bridge = segment
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
        # Ear clipping: while polygon has more than 3 vertices, find and clip an ear.
        ears_list: list[Ear] = []
        while len(points) > 3:
            titanic: Polygon = Polygon(list(points))
            n: int = len(points)
            found: int | None = None
            for j in range(n):
                left_pt: Point = points[j - 1]
                center_pt: Point = points[j]
                right_pt: Point = points[(j + 1) % n]
                walk: Walk = Walk(start=left_pt, center=center_pt, end=right_pt)
                if walk.is_collinear():
                    continue
                if not walk.is_ccw():
                    continue
                diagonal: Segment = left_pt.to(right_pt)
                if not titanic.contains(diagonal, inclusive=True):
                    continue
                tri: Polygon = Polygon([left_pt, center_pt, right_pt])
                if any(tri.contains(points[k], inclusive=False) for k in range(n) if k not in ((j - 1) % n, j, (j + 1) % n)):
                    continue
                found = j
                ears_list.append(Ear([left_pt, center_pt, right_pt]))
                break
            if found is None:
                raise EarClippingFailureError(f"No ear found for: {points}")
            # Remove ear tip from polygon and continue.
            points = Polygon([points[i] for i in range(n) if i != found])
        # Add final triangle as last ear (ccw or reversed if cw).
        if len(points) == 3:
            path: Walk = Walk(start=points[0], center=points[1], end=points[2])
            if path.is_ccw():
                ears_list.append(Ear([points[0], points[1], points[2]]))
            else:
                ears_list.append(Ear([points[2], points[1], points[0]]))
        # Build initial convex components from ears; merge adjacent pairs by largest area until no merge possible.
        components: list[ConvexComponent] = [ConvexComponent(list(ear)) for ear in ears_list]
        while True:
            # Index components by edge (frozenset of endpoints) to find adjacent pairs.
            components_by_edge: defaultdict[frozenset[Point], list[ConvexComponent]] = defaultdict(list)
            for comp in components:
                for edge in comp.edges:
                    key: frozenset[Point] = frozenset({edge[0], edge[1]})
                    components_by_edge[key].append(comp)
            best_area: Decimal | None = None
            best_merged: ConvexComponent | None = None
            best_pair: tuple[ConvexComponent, ConvexComponent] | None = None
            # Try merging each component with an adjacent one; keep the merge with largest area.
            for comp in components:
                adjacent: set[ConvexComponent] = {
                    other for edge in comp.edges for other in components_by_edge[frozenset({edge[0], edge[1]})] if other is not comp
                }
                for other in adjacent:
                    try:
                        merged_cc: ConvexComponent = comp + other
                    except (ValidationError, PolygonsDoNotShareEdgeError):
                        continue
                    if best_area is None or abs(merged_cc.signed_area) > best_area:
                        best_area = abs(merged_cc.signed_area)
                        best_merged = merged_cc
                        best_pair = (comp, other)
            if best_pair is None or best_merged is None:
                break
            # Replace the two components with the merged one.
            components.remove(best_pair[0])
            components.remove(best_pair[1])
            components.append(best_merged)
        return {"convex_components": [cc.serialize() for cc in components]}


class GuardPlacementStep(SequenceStep):
    """
    Guard placement step. Idempotent: given the same job and inputs, running
    multiple times produces the same outcome. Recomputes stitch, ear clipping,
    convex optimization, then greedy guard placement + post-process (same logic
    as lab ArtGallery.guards). Returns guards (list of Point) and visibility
    (list of list of points; visibility[i] = points visible by guards[i]).
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        # Parse boundary and obstacles from job stdin.
        boundary: Polygon = Polygon.unserialize(self.job.stdin.get("boundary"))
        obstacles: list[Polygon] = [Polygon.unserialize(obstacle) for obstacle in (self.job.stdin.get("obstacles") or [])]
        stitched: Polygon
        if not obstacles:
            stitched = boundary
        else:
            # Sort obstacles by rightmost vertex (desc) and stitch each to the current polygon.
            obstacles = sorted(obstacles, key=lambda obstacle: (obstacle.rightmost.x, obstacle.rightmost.y), reverse=True)
            stitched = Polygon(list(boundary))
            edges: list[Segment] = list(stitched.edges)
            for obstacle in obstacles:
                obstacle.sort("cw")
                anchors: list[Point] = sorted(list(obstacle), key=lambda point: (point.x, point.y), reverse=True)
                bridge: Segment | None = None
                anchor: Point | None = None
                # Find shortest valid bridge from polygon to obstacle anchor (bucket of candidates).
                for anchor in anchors:
                    bridge = None
                    bucket: list[Segment] = []
                    for candidate in stitched << stitched.rightmost:
                        if candidate == anchor:
                            continue
                        segment: Segment = candidate.to(anchor)
                        if not boundary.contains(segment, inclusive=True):
                            continue
                        if any(other.intersects(segment, inclusive=False) for other in obstacles):
                            continue
                        if any(
                            Walk(start=edge[0], center=edge[1], end=segment[0]).is_collinear()
                            and Walk(start=edge[0], center=edge[1], end=segment[1]).is_collinear()
                            for edge in boundary.edges
                            if not edge.connects(segment)
                        ):
                            continue
                        if any(edge.intersects(segment) for edge in edges if not edge.connects(segment)):
                            continue
                        bucket.append(segment)
                        bucket.sort(key=lambda s: s.size)
                        bucket = bucket[:STITCH_BUCKET_SIZE]
                        if len(bucket) >= STITCH_BUCKET_SIZE:
                            bridge = bucket[0]
                            break
                        if bridge is None or segment.size < bridge.size:
                            bridge = segment
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
                left: Polygon = Polygon(list(stitched >> vertex))
                right: Polygon = Polygon(list(obstacle << anchor))
                if not left.is_ccw():
                    raise StitchWinnerSubsequenceError("Left is not CCW; cannot stitch")
                if not right.is_cw():
                    raise StitchWinnerSubsequenceError("Right is not CW; cannot stitch")
                merged: list[Point] = list(left) + list(right) + [anchor, vertex]
                stitched = Polygon(merged)
                edges = list(stitched.edges)
            stitched.sort("ccw")
        # Ear clipping: while polygon has more than 3 vertices, find and clip an ear.
        points_ear: Polygon = Polygon(list(stitched))
        ears_guard: list[Ear] = []
        while len(points_ear) > 3:
            titanic: Polygon = Polygon(list(points_ear))
            n: int = len(points_ear)
            found: int | None = None
            for j in range(n):
                left_pt: Point = points_ear[j - 1]
                center_pt: Point = points_ear[j]
                right_pt: Point = points_ear[(j + 1) % n]
                walk: Walk = Walk(start=left_pt, center=center_pt, end=right_pt)
                if walk.is_collinear():
                    continue
                if not walk.is_ccw():
                    continue
                diagonal: Segment = left_pt.to(right_pt)
                if not titanic.contains(diagonal, inclusive=True):
                    continue
                tri: Polygon = Polygon([left_pt, center_pt, right_pt])
                if any(tri.contains(points_ear[k], inclusive=False) for k in range(n) if k not in ((j - 1) % n, j, (j + 1) % n)):
                    continue
                found = j
                ears_guard.append(Ear([left_pt, center_pt, right_pt]))
                break
            if found is None:
                raise EarClippingFailureError(f"No ear found for: {points_ear}")
            # Remove ear tip from polygon and continue.
            points_ear = Polygon([points_ear[i] for i in range(n) if i != found])
        # Add final triangle as last ear (ccw or reversed if cw).
        if len(points_ear) == 3:
            path: Walk = Walk(start=points_ear[0], center=points_ear[1], end=points_ear[2])
            if path.is_ccw():
                ears_guard.append(Ear([points_ear[0], points_ear[1], points_ear[2]]))
            else:
                ears_guard.append(Ear([points_ear[2], points_ear[1], points_ear[0]]))
        # Build convex components from ears; merge adjacent pairs by largest area until no merge possible.
        components_guard: list[ConvexComponent] = [ConvexComponent(list(ear)) for ear in ears_guard]
        while True:
            # Index components by edge to find adjacent pairs.
            components_by_edge_guard: defaultdict[frozenset, list[ConvexComponent]] = defaultdict(list)
            for comp in components_guard:
                for edge in comp.edges:
                    key = frozenset({edge[0], edge[1]})
                    components_by_edge_guard[key].append(comp)
            best_area_guard: Decimal | None = None
            best_merged_guard: ConvexComponent | None = None
            best_pair_guard: tuple[ConvexComponent, ConvexComponent] | None = None
            # Try merging each component with an adjacent one; keep the merge with largest area.
            for comp in components_guard:
                adjacent = {other for edge in comp.edges for other in components_by_edge_guard[frozenset({edge[0], edge[1]})] if other is not comp}
                for other in adjacent:
                    try:
                        merged = comp + other
                    except (ValidationError, PolygonsDoNotShareEdgeError):
                        continue
                    if best_area_guard is None or abs(merged.signed_area) > best_area_guard:
                        best_area_guard = abs(merged.signed_area)
                        best_merged_guard = merged
                        best_pair_guard = (comp, other)
            if best_pair_guard is None or best_merged_guard is None:
                break
            # Replace the two components with the merged one.
            components_guard.remove(best_pair_guard[0])
            components_guard.remove(best_pair_guard[1])
            components_guard.append(best_merged_guard)
        # Greedy guard placement: candidates = stitched vertices; pick guard that sees most remaining components.
        candidates: list[Point] = list(stitched)
        remaining_components: set[ConvexComponent] = set(components_guard)
        guards: list[Point] = []
        while remaining_components:
            best_guard: Point | None = None
            best_count: int = -1
            # Choose candidate that sees the most uncovered components.
            for g in candidates:
                count: int = 0
                for comp in remaining_components:
                    if g in list(comp):
                        count += 1
                    elif all(
                        boundary.contains(g.to(point), inclusive=True)
                        and not any(obstacle.intersects(g.to(point), inclusive=False) for obstacle in obstacles)
                        and not any(obstacle.contains(g.to(point).midpoint, inclusive=False) for obstacle in obstacles)
                        for point in comp
                    ):
                        count += 1
                if count > best_count:
                    best_count = count
                    best_guard = g
            if best_guard is None or best_count == 0:
                raise GuardCoverageFailureError("Failed to cover all convex components.")
            guards.append(best_guard)
            candidates.remove(best_guard)
            # Mark components now covered by this guard and remove from remaining.
            seen: set[ConvexComponent] = set()
            for comp in remaining_components:
                if best_guard in list(comp):
                    seen.add(comp)
                elif all(
                    boundary.contains(best_guard.to(point), inclusive=True)
                    and not any(obstacle.intersects(best_guard.to(point), inclusive=False) for obstacle in obstacles)
                    and not any(obstacle.contains(best_guard.to(point).midpoint, inclusive=False) for obstacle in obstacles)
                    for point in comp
                ):
                    seen.add(comp)
            remaining_components -= seen
        # Post-process: remove redundant guards whose visibility is contained in the union of the others.
        removed: bool = True
        while removed:
            removed = False
            visibility_by_guard: list[list[Point]] = []
            for g in guards:
                vis: list[Point] = [
                    point
                    for point in stitched
                    if g == point
                    or (
                        boundary.contains(g.to(point), inclusive=True)
                        and not any(obstacle.intersects(g.to(point), inclusive=False) for obstacle in obstacles)
                        and not any(obstacle.contains(g.to(point).midpoint, inclusive=False) for obstacle in obstacles)
                    )
                ]
                visibility_by_guard.append(vis)
            uncovereed: set[Point] = set(stitched) - set().union(*(set(vis) for vis in visibility_by_guard))
            if uncovereed:
                raise GuardCoverageFailureError("Failed to cover points.")
            # If a guard's visible set is subset of the union of others, remove that guard.
            for i, g in enumerate(guards):
                other_union: set[Point] = set().union(*(set(visibility_by_guard[j]) for j in range(len(guards)) if j != i))
                if set(visibility_by_guard[i]).issubset(other_union):
                    guards.pop(i)
                    removed = True
                    break
        # Build final visibility list (points visible by each guard) and return.
        visibility_final: list[list[Point]] = []
        for g in guards:
            vis = [
                point
                for point in stitched
                if g == point
                or (
                    boundary.contains(g.to(point), inclusive=True)
                    and not any(obstacle.intersects(g.to(point), inclusive=False) for obstacle in obstacles)
                    and not any(obstacle.contains(g.to(point).midpoint, inclusive=False) for obstacle in obstacles)
                )
            ]
            visibility_final.append(vis)
        return {
            "guards": [g.serialize() for g in guards],
            "visibility": [[point.serialize() for point in vis] for vis in visibility_final],
        }
