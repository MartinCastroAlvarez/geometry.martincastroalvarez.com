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

from abc import ABC
from abc import abstractmethod
from functools import cached_property
from typing import Any
from typing import Type

from attributes import Identifier
from attributes import Signature
from enums import Status
from enums import StepName
from exceptions import PolygonNotSimpleError
from exceptions import StepNotHandledError
from geometry import Polygon
from models import Job
from models import User
from repositories import JobsRepository


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
    are created with status SUCCESS momentarily so the parent's REPORT does not block.
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
                status=Status.SUCCESS,
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
        stdout: dict[str, Any] = {"step:art_gallery": "success"}
        if "boundary" in self.job.stdin:
            stdout["boundary"] = self.job.stdin["boundary"]
        if "obstacles" in self.job.stdin:
            stdout["obstacles"] = self.job.stdin["obstacles"]
        return stdout


class ValidationPolygonStep(SequenceStep):
    """
    Validates boundary and obstacles using api/geometry (same logic as lab ArtGallery.validate()).
    On success returns step result and calls broadcast(). We do not catch Exception; let failures
    raise so StartTask can handle them (set job status, stderr, etc.).
    """

    def parse_boundary_and_obstacles(self, stdin: dict[str, Any]) -> tuple[Polygon, list[Polygon]]:
        """Unserialize boundary and obstacles from job stdin (list or { points })."""
        boundary_raw: Any = stdin.get("boundary")
        obstacles_raw: Any = stdin.get("obstacles")
        if boundary_raw is None:
            raise ValueError("boundary is required")
        if isinstance(boundary_raw, dict) and "points" in boundary_raw:
            boundary_raw = boundary_raw["points"]
        if not isinstance(boundary_raw, list):
            raise ValueError("boundary must be a list of points or an object with key 'points'")
        boundary_poly: Polygon = Polygon.unserialize(boundary_raw)
        obstacle_list: list[Any] = obstacles_raw if isinstance(obstacles_raw, list) else []
        obstacle_polys: list[Polygon] = []
        for obs in obstacle_list:
            if isinstance(obs, dict) and "points" in obs:
                pts = obs["points"]
            else:
                pts = obs
            if isinstance(pts, list):
                obstacle_polys.append(Polygon.unserialize(pts))
        return boundary_poly, obstacle_polys

    def validate_polygons_geometry(self, boundary: Polygon, obstacles: list[Polygon]) -> None:
        """
        Same logic as lab ArtGallery.validate(): obstacles strictly inside boundary,
        no obstacle edge touching/intersecting boundary (except not shared), no vertex on boundary, no obstacle-over-obstacle overlap.
        Raises PolygonNotSimpleError on failure.
        """
        for obstacle in obstacles:
            for point in obstacle:
                if not boundary.contains(point, inclusive=False):
                    raise PolygonNotSimpleError(f"Obstacle vertex is not strictly inside the boundary ({boundary}).")
            for edge in obstacle.edges:
                for boundary_edge in boundary.edges:
                    if edge.intersects(boundary_edge, inclusive=True) and not edge.connects(boundary_edge):
                        raise PolygonNotSimpleError("Obstacle edge intersects or touches boundary.")
            for point in obstacle:
                for boundary_edge in boundary.edges:
                    if boundary_edge.contains(point, inclusive=True):
                        raise PolygonNotSimpleError("Obstacle has a vertex on the boundary.")
        for i, obstacle in enumerate(obstacles):
            for other in obstacles[i + 1 :]:
                if obstacle.intersects(other, inclusive=True):
                    raise PolygonNotSimpleError("Obstacles intersect or touch.")

    def run(self, **kwargs: Any) -> dict[str, Any]:
        # Do not try/except Exception here. Let validation failures raise; StartTask handles exceptions.
        boundary, obstacles = self.parse_boundary_and_obstacles(self.job.stdin)
        self.validate_polygons_geometry(boundary, obstacles)
        return {"step:validate_polygons": "success"}


class StitchingStep(SequenceStep):
    """
    Stitching step. Idempotent: given the same job and inputs, running
    multiple times produces the same outcome.
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        out: dict[str, Any] = {"step:stitching": "success"}
        return out


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
