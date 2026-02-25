"""
Job create and update mutations.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any
from typing import TypedDict

from exceptions import UnauthorizedError
from exceptions import ValidationError
from index.indexed import Indexed
from index.jobs import JobsPrivateIndex
from messages import Message
from messages import Queue
from models import Job
from repositories.jobs import JobsRepository
from attributes import Action
from attributes import Identifier
from attributes import Countdown

from mutations.base import Mutation
from mutations.base import MutationInput
from mutations.utils import coerce_boundary
from mutations.utils import coerce_obstacles

queue = Queue()


class JobMutationInput(MutationInput):
    """Create job: boundary and obstacles; id is hash (idempotent)."""

    boundary: list[tuple[str, str]]
    obstacles: list[list[tuple[str, str]]]


class JobUpdateMutationInput(MutationInput, total=False):
    """Update job (e.g. status) by id."""

    id: str
    status: str


class JobMutation(Mutation[JobMutationInput]):
    """Create job (idempotent id from boundary+obstacles), save, enqueue run, update job index."""

    def validate(self, body: dict[str, Any] | None = None) -> JobMutationInput:
        if not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        payload = body or {}
        boundary = payload.get("boundary")
        obstacles = payload.get("obstacles")
        if not boundary or not isinstance(boundary, list):
            raise ValidationError("boundary is required and must be a list of points")
        if obstacles is not None and not isinstance(obstacles, list):
            raise ValidationError("obstacles must be a list of obstacle polygons")
        return JobMutationInput(
            boundary=coerce_boundary(boundary),
            obstacles=coerce_obstacles(obstacles or []),
        )

    def mutate(self, validated_input: JobMutationInput) -> dict[str, Any]:
        boundary = validated_input["boundary"]
        obstacles = validated_input["obstacles"]
        payload = {"boundary": boundary, "obstacles": obstacles}
        id_source = json.dumps(payload, sort_keys=True)
        job_id = hashlib.sha256(id_source.encode()).hexdigest()
        job = Job(
            id=Identifier(job_id),
            parent_id="",
            children_ids=[],
            status="pending",
            task="art_gallery",
            stdin=payload,
            stdout={},
            meta={},
            stderr={},
        )
        repo = JobsRepository(user=self.user)
        repo.save(job)
        email = self.user.email
        if email is None:
            raise UnauthorizedError("User must be authenticated")
        queue.put(Message(action=Action(Action.RUN), job_id=job_id, user_email=email))
        index = JobsPrivateIndex(user_email=email)
        index.save(Indexed(index_id=Identifier(str(Countdown.from_timestamp(job.created_at))), real_id=job.id))
        return job.to_dict()


class JobUpdateMutation(Mutation[JobUpdateMutationInput]):
    """Update job (e.g. status); id from path."""

    def validate(self, body: dict[str, Any] | None = None) -> JobUpdateMutationInput:
        if not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        payload = body or {}
        identifier_raw = payload.get("id")
        if not identifier_raw or not isinstance(identifier_raw, str):
            raise ValidationError("id is required and must be a non-empty string")
        out: JobUpdateMutationInput = {"id": Identifier(identifier_raw)}
        if "status" in payload and payload["status"] is not None:
            out["status"] = str(payload["status"])
        return out

    def mutate(self, validated_input: JobUpdateMutationInput) -> dict[str, Any]:
        identifier = validated_input["id"]
        repo = JobsRepository(user=self.user)
        job = repo.get(identifier)
        if validated_input.get("status") is not None:
            job.status = validated_input["status"]
            repo.save(job)
        return job.to_dict()
