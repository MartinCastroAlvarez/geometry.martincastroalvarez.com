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
from typing import Any

from attributes import Email
from attributes import Identifier
from attributes import Signature
from enums import Action
from enums import Status
from enums import StepName
from messages import Message
from messages import Queue
from models import Job
from models import User
from repositories import JobsRepository


class Step(ABC):
    """
    Abstract pipeline step. Receives a Job and user_email; run() returns a dict
    merged into job.stdout. Steps are idempotent: same job + inputs => same result.
    """

    def __init__(self, job: Job, user_email: Email) -> None:
        self.job: Job = job
        self.user_email: Email = user_email

    @abstractmethod
    def run(self, **kwargs: Any) -> dict[str, Any]:
        """
        Execute the step. Return a dict to merge into job.stdout.
        May mutate self.job (e.g. children_ids). Caller persists job after run().
        """
        raise NotImplementedError


class ArtGalleryStep(Step):
    """
    Art gallery step: enqueues REPORT for the current job and creates child jobs
    (visibility_matrix, stitching, ear_clipping, convex_component_optimization,
    guard_placement) with deterministic ids. Children are created with status
    SUCCESS momentarily so the parent's REPORT does not block waiting for them.
    """

    def run(self, **kwargs: Any) -> dict[str, Any]:
        queue: Queue = Queue()
        user: User = User(email=self.user_email)
        repo: JobsRepository = JobsRepository(user=user)

        child_step_names: list[StepName] = [
            StepName.VISIBILITY_MATRIX,
            StepName.STITCHING,
            StepName.EAR_CLIPPING,
            StepName.CONVEX_COMPONENT_OPTIMIZATION,
            StepName.GUARD_PLACEMENT,
        ]
        child_ids: list[Identifier] = []

        for step_name in child_step_names:
            child_id: Identifier = Identifier(Signature(f"{self.job.id}_{step_name.value}"))
            if repo.exists(child_id):
                child_ids.append(child_id)
                continue
            child: Job = Job(
                id=child_id,
                parent_id=self.job.id,
                status=Status.SUCCESS,
                step_name=step_name,
                stdin=dict(self.job.stdin),
            )
            repo.save(child)
            child_ids.append(child_id)

        self.job.children_ids = child_ids

        message: Message = Message(
            action=Action.REPORT,
            job_id=self.job.id,
            user_email=self.user_email,
            meta=kwargs if kwargs else None,
        )
        queue.put(message)

        return {"step:art_gallery": "success"}


class VisibilityMatrixStep(Step):
    """Visibility matrix step. Idempotent: same job => same output."""

    def run(self, **kwargs: Any) -> dict[str, Any]:
        return {"step:visibility_matrix": "success"}


class StitchingStep(Step):
    """Stitching step. Idempotent: same job => same output."""

    def run(self, **kwargs: Any) -> dict[str, Any]:
        return {"step:stitching": "success"}


class EarClippingStep(Step):
    """Ear clipping step. Idempotent: same job => same output."""

    def run(self, **kwargs: Any) -> dict[str, Any]:
        return {"step:ear_clipping": "success"}


class ConvexComponentOptimizationStep(Step):
    """Convex component optimization step. Idempotent: same job => same output."""

    def run(self, **kwargs: Any) -> dict[str, Any]:
        return {"step:convex_component_optimization": "success"}


class GuardPlacementStep(Step):
    """Guard placement step. Idempotent: same job => same output."""

    def run(self, **kwargs: Any) -> dict[str, Any]:
        return {"step:guard_placement": "success"}
