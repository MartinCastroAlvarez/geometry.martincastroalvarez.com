"""
Job create mutation.
"""

from __future__ import annotations

from typing import Any

from attributes import Countdown
from attributes import Identifier
from attributes import Signature
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
from mutations.response import JobMutationResponse
from repositories.jobs import JobsRepository
from structs import Table

queue = Queue()


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
        return job.serialize()
