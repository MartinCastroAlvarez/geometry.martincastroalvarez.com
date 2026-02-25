"""
Job details query.
"""

from __future__ import annotations

from typing import Any

from exceptions import UnauthorizedError
from exceptions import ValidationError
from repositories.jobs import JobsRepository

from queries.base import Query
from queries.base import QueryInput


class JobDetailsQueryInput(QueryInput):
    """Input for job by id."""

    id: str


class JobDetailsQuery(Query[JobDetailsQueryInput]):
    """Get a single job by id (must be owner)."""

    def validate(self, body: dict[str, Any] | None = None) -> JobDetailsQueryInput:
        if not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        payload = body or {}
        identifier = payload.get("id")
        if not identifier or not isinstance(identifier, str):
            raise ValidationError("id is required and must be a non-empty string")
        return JobDetailsQueryInput(id=identifier)

    def query(self, validated_input: JobDetailsQueryInput) -> dict[str, Any]:
        repo = JobsRepository(user=self.user)
        job = repo.get(validated_input["id"])
        return job.to_dict()
