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
from functools import cached_property
from typing import Any
from typing import Type

from attributes import Identifier
from attributes import Signature
from enums import Status
from enums import StepName
from exceptions import BridgeFailureError
from exceptions import PolygonNotSimpleError
from exceptions import StepNotHandledError
from exceptions import StitchWinnerSubsequenceError
from exceptions import ValidationBoundaryNotCCWError
from exceptions import ValidationObstacleNotCWError
from geometry.segment import Segment
from geometry.walk import Walk
from models import Job
from models import User
from repositories import JobsRepository

from geometry import Point
from geometry import Polygon

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
            raise StepNotHandledError(f"Step cannot be handled: {step_name.value}")
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
            "step:art_gallery": "success",
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
        return {"step:validate_polygons": "success"}


class StitchingStep(SequenceStep):
    """
    Stitching step: merges boundary and obstacles into a single polygon (stitched)
    by sorting obstacles by rightmost vertex and bridging each to the current outer
    polygon. Same logic as lab ArtGallery.points. Idempotent: same job and inputs
    yield the same stitched polygon. Emits "stitched" (serialized Polygon) in stdout.
    """

    def __init__(self, job: Job, user: User) -> None:
        super().__init__(job, user)
        self.boundary: Polygon | None = None
        self.obstacles: list[Polygon] = []
        self.points: Polygon | None = None

    def sort(self) -> None:
        """Sort obstacles in place by rightmost vertex (x, y) descending for bridge order."""
        self.obstacles.sort(key=lambda o: (o.rightmost.x, o.rightmost.y), reverse=True)

    def run(self, **kwargs: Any) -> dict[str, Any]:
        # Parse boundary and obstacles from job stdin (Polygon.unserialize may raise).
        self.boundary = Polygon.unserialize(self.job.stdin.get("boundary"))
        self.obstacles = [Polygon.unserialize(obstacle) for obstacle in (self.job.stdin.get("obstacles") or [])]

        # No obstacles: stitched result is the boundary; return immediately.
        if not self.obstacles:
            self.points = self.boundary
            return {"step:stitching": "success", "stitched": self.points.serialize()}

        # Sort obstacles by rightmost vertex (desc) and init working polygon and its edges.
        self.sort()
        logger.info("Stitching %d obstacles to boundary (%d points).", len(self.obstacles), len(self.boundary))
        points: Polygon = Polygon(list(self.boundary))
        edges: list[Segment] = list(points.edges)

        for obstacle in self.obstacles:
            # Normalize obstacle to CW and take rightmost vertex as bridge anchor.
            obstacle_points: Polygon = obstacle if obstacle.is_cw() else Polygon(list(~obstacle))
            anchor: Point = obstacle_points.rightmost
            bridge: Segment | None = None

            # Find shortest valid bridge from current polygon to anchor (inside boundary, no crossings).
            for candidate in points:
                if candidate == anchor:
                    continue
                if candidate.x < anchor.x or candidate.y < anchor.y:
                    continue
                segment: Segment = candidate.to(anchor)
                if not self.boundary.contains(segment, inclusive=True):
                    continue
                if any(
                    Walk(start=edge[0], center=edge[1], end=segment[0]).is_collinear()
                    and Walk(start=edge[0], center=edge[1], end=segment[1]).is_collinear()
                    for edge in self.boundary.edges
                    if not edge.connects(segment)
                ):
                    continue
                if any(other.intersects(segment, inclusive=False) for other in self.obstacles if other is not obstacle):
                    continue
                if any(edge.intersects(segment) for edge in edges if not edge.connects(segment)):
                    continue
                if bridge is None or segment.size < bridge.size:
                    bridge = segment

            if bridge is None:
                raise BridgeFailureError(f"No valid bridge found for obstacle: {obstacle}")

            # Reject if bridge is a contiguous subsequence of polygon or obstacle (cannot stitch).
            vertex: Point = bridge[0]
            if bridge in points:
                raise StitchWinnerSubsequenceError("Winner is a subsequence of boundary points; cannot stitch")
            if bridge in obstacle_points:
                raise StitchWinnerSubsequenceError("Winner is a subsequence of obstacle; cannot stitch")

            # Rotate polygon so vertex is last, obstacle so anchor is first; require CCW/CW; merge and update.
            left: Polygon = Polygon(list(points >> vertex))
            right: Polygon = Polygon(list(obstacle_points << anchor))
            if not left.is_ccw():
                raise StitchWinnerSubsequenceError("Left is not CCW; cannot stitch")
            if not right.is_cw():
                raise StitchWinnerSubsequenceError("Right is not CW; cannot stitch")
            merged: list[Point] = list(left) + list(right) + [anchor, vertex]
            points = Polygon(merged)
            edges = list(points.edges)

        # Ensure final polygon is CCW; store and return serialized stitched polygon.
        if not points.is_ccw():
            points = Polygon(list(~points))
        self.points = points
        return {"step:stitching": "success", "stitched": self.points.serialize()}


class EarClippingStep(SequenceStep):
    """
    Ear clipping step. Idempotent: given the same job and inputs, running
    multiple times produces the same outcome.
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        out: dict[str, Any] = {"step:ear_clipping": "success"}
        return out


class ConvexComponentOptimizationStep(SequenceStep):
    """
    Convex component optimization step. Idempotent: given the same job and
    inputs, running multiple times produces the same outcome.
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        out: dict[str, Any] = {"step:convex_component_optimization": "success"}
        return out


class GuardPlacementStep(SequenceStep):
    """
    Guard placement step. Idempotent: given the same job and inputs, running
    multiple times produces the same outcome.
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        out: dict[str, Any] = {"step:guard_placement": "success"}
        return out
