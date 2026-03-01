"""
Job create and update mutations.

Title
-----
Job Mutations

Context
-------
JobMutation creates a job: validates boundary and obstacles, builds
idempotent job id from Signature(boundary+obstacles), saves to JobsRepository,
enqueues START message, and adds entry to JobsPrivateIndex (Countdown key).
JobUpdateMutation updates job meta (e.g. title); if meta contains "title"
and the user has a published gallery for that job, the gallery title is
updated. Both require authenticated user (PrivateControllerMixin). Used by
api.api (ROUTES) for POST and PATCH on v1/jobs and v1/jobs/.

Examples:
>>> POST v1/jobs with body { boundary, obstacles } -> JobMutation
>>> PATCH v1/jobs/:id with body { meta: { title: "..." } } -> JobUpdateMutation
"""

from __future__ import annotations

import logging
from typing import Any

from attributes import Countdown
from attributes import Identifier
from attributes import Signature
from attributes import Title
from controllers import PrivateControllerMixin
from enums import Action
from exceptions import PolygonValidationError
from exceptions import UnauthorizedError
from exceptions import ValidationError
from geometry import Polygon
from indexes import JobsPrivateIndex
from logger import get_logger
from messages import Message
from messages import Queue
from models import ArtGallery
from models import Job
from mutations.base import Mutation
from mutations.request import JobMutationRequest
from mutations.request import JobUpdateMutationRequest
from mutations.response import JobMutationResponse
from mutations.utils import gallery_id_from_job_and_user
from repositories import ArtGalleryRepository
from repositories import JobsRepository
from structs import Table
from validators import PolygonValidator

queue: Queue = Queue()
logger: logging.Logger = get_logger(__name__)


class JobMutation(PrivateControllerMixin, Mutation):
    """Create job (idempotent id from boundary+obstacles), save, enqueue run, update job index."""

    def validate(self, body: dict[str, Any]) -> JobMutationRequest:
        super().validate(body)
        boundary = body.get("boundary")
        obstacles = body.get("obstacles")
        if not boundary or not isinstance(boundary, list):
            raise ValidationError("boundary is required and must be a list of points")
        if obstacles is not None and not isinstance(obstacles, list):
            raise ValidationError("obstacles must be a list of obstacle polygons")
        return JobMutationRequest(
            boundary=Polygon.unserialize(boundary),
            obstacles=Table.unserialize([Polygon.unserialize(obstacle) for obstacle in (obstacles or []) if isinstance(obstacle, list)]),
        )

    def execute(self, validated_input: JobMutationRequest) -> JobMutationResponse:
        boundary: Polygon = validated_input["boundary"]
        obstacles: Table[Polygon] = validated_input["obstacles"]
        # Fail fast: run polygon validation and raise if any check fails.
        validator: PolygonValidator = PolygonValidator()
        validation_result: dict[str, Any] = validator.execute({"boundary": boundary, "obstacles": obstacles})
        failed: list[str] = [k for k, v in validation_result.items() if not k.endswith(".note") and v == "failed"]
        if failed:
            raise PolygonValidationError("Polygon validation failed: " + ", ".join(failed))
        job_id: Identifier = Identifier(Signature(f"{hash(boundary)}_{hash(obstacles)}"))
        job: Job = Job(
            id=job_id,
            stdin={
                "boundary": boundary.serialize(),
                "obstacles": [poly.serialize() for poly in obstacles],
            },
        )
        repo: JobsRepository = JobsRepository(user=self.user)
        repo.save(job)
        email: str | None = self.user.email
        if email is None:
            raise UnauthorizedError("User must be authenticated")
        message: Message = Message(action=Action.START, job_id=job.id, user_email=email)
        queue.put(message)
        JobsPrivateIndex(user_email=email).index(
            index_id=Identifier(Countdown.from_timestamp(job.created_at)),
            real_id=job.id,
        )
        logger.info("JobMutation.mutate() | created job_id=%s user=%s", job.id, email)
        return job.serialize()


class JobUpdateMutation(PrivateControllerMixin, Mutation):
    """Update job metadata; sync title to gallery if published."""

    def validate(self, body: dict[str, Any]) -> JobUpdateMutationRequest:
        super().validate(body)
        meta = body.get("meta")
        if meta is None:
            raise ValidationError("meta is required")
        if not isinstance(meta, dict):
            raise ValidationError("meta must be a dict")
        meta_str: dict[str, str] = {}
        for k, v in meta.items():
            if not isinstance(k, str):
                raise ValidationError("meta keys must be strings")
            if v is not None and not isinstance(v, str):
                raise ValidationError("meta values must be strings")
            meta_str[k] = str(v) if v is not None else ""
        return JobUpdateMutationRequest(
            job_id=Identifier(body.get("id")),
            meta=meta_str,
        )

    def execute(self, validated_input: JobUpdateMutationRequest) -> JobMutationResponse:
        job_id: Identifier = validated_input["job_id"]
        meta: dict[str, str] = validated_input["meta"]
        email: str | None = self.user.email
        if email is None:
            raise UnauthorizedError("User must be authenticated")
        repo_job: JobsRepository = JobsRepository(user=self.user)
        job: Job = repo_job.get(job_id)
        job.meta = {**job.meta, **meta}
        repo_job.save(job)
        if "title" in meta:
            gallery_repo: ArtGalleryRepository = ArtGalleryRepository()
            gallery_id: Identifier = gallery_id_from_job_and_user(job_id, email)
            if gallery_repo.exists(gallery_id):
                gallery: ArtGallery = gallery_repo.get(gallery_id)
                gallery.title = Title(meta["title"])
                gallery_repo.save(gallery)
        logger.info("JobUpdateMutation.mutate() | updated job_id=%s", job.id)
        return job.serialize()
