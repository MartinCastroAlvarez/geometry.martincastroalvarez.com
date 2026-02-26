"""
Job create and update mutations.
"""

from __future__ import annotations

from typing import Any

from attributes import Countdown
from attributes import Identifier
from attributes import Signature
from attributes import Title
from enums import Action
from exceptions import UnauthorizedError
from exceptions import ValidationError
from geometry import Polygon
from indexes.indexed import Indexed
from indexes.jobs import JobsPrivateIndex
from messages import Message
from messages import Queue
from models import Job
from mutations.private import PrivateMutation
from mutations.request import JobMutationRequest
from mutations.request import JobUpdateMutationRequest
from mutations.response import JobMutationResponse
from mutations.utils import gallery_id_from_job_and_user
from repositories.gallery import ArtGalleryRepository
from repositories.jobs import JobsRepository
from structs import Table

from api.logger import get_logger

queue = Queue()
logger = get_logger(__name__)


class JobMutation(PrivateMutation[JobMutationRequest, JobMutationResponse]):
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
            obstacles=Table.unserialize([Polygon.unserialize(obs) for obs in (obstacles or []) if isinstance(obs, list)]),
        )

    def mutate(self, validated_input: JobMutationRequest) -> JobMutationResponse:
        boundary = validated_input["boundary"]
        obstacles = validated_input["obstacles"]
        job_id = Identifier(Signature(f"{hash(boundary)}_{hash(obstacles)}"))
        job = Job(
            id=job_id,
            stdin={
                "boundary": boundary.serialize(),
                "obstacles": [poly.serialize() for poly in obstacles],
            },
        )
        repo = JobsRepository(user=self.user)
        repo.save(job)
        email = self.user.email
        if email is None:
            raise UnauthorizedError("User must be authenticated")
        queue.put(Message(action=Action.START, job_id=job.id, user_email=email))
        index = JobsPrivateIndex(user_email=email)
        index.save(
            Indexed(
                index_id=Identifier(Countdown.from_timestamp(job.created_at)),
                real_id=job.id,
            )
        )
        logger.info("JobMutation.mutate() | created job_id=%s user=%s", job.id, email)
        return job.serialize()


class JobUpdateMutation(PrivateMutation[JobUpdateMutationRequest, JobMutationResponse]):
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

    def mutate(self, validated_input: JobUpdateMutationRequest) -> JobMutationResponse:
        job_id = validated_input["job_id"]
        meta = validated_input["meta"]
        email = self.user.email
        if email is None:
            raise UnauthorizedError("User must be authenticated")
        repo_job = JobsRepository(user=self.user)
        job = repo_job.get(job_id)
        job.meta = {**job.meta, **meta}
        repo_job.save(job)
        if "title" in meta:
            gallery_repo = ArtGalleryRepository()
            gallery_id = gallery_id_from_job_and_user(job_id, email)
            if gallery_repo.exists(gallery_id):
                gallery = gallery_repo.get(gallery_id)
                gallery.title = Title(meta["title"])
                gallery_repo.save(gallery)
        logger.info("JobUpdateMutation.mutate() | updated job_id=%s", job.id)
        return job.serialize()
