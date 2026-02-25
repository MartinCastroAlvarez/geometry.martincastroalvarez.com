"""
Job details query.
"""

from __future__ import annotations

from typing import Any

from repositories.jobs import JobsRepository
from attributes import Identifier

from queries.private import PrivateQuery
from queries.request import DetailsQueryRequest
from queries.response import DetailsQueryResponse


class JobDetailsQueryResponse(DetailsQueryResponse):
    """Details response: single job (JobDict shape)."""

    id: str
    parent_id: str | None
    children_ids: list[str]
    status: str
    stage: str
    stdin: dict[str, Any]
    stdout: dict[str, Any]
    meta: dict[str, Any]
    stderr: dict[str, Any]
    created_at: str
    updated_at: str


class JobDetailsQuery(PrivateQuery[DetailsQueryRequest, JobDetailsQueryResponse]):
    """Get a single job by id (must be owner)."""

    def _validate_body(self, body: dict[str, Any]) -> DetailsQueryRequest:
        return DetailsQueryRequest(id=Identifier(body.get("id")))

    def query(self, validated_input: DetailsQueryRequest) -> JobDetailsQueryResponse:
        repo = JobsRepository(user=self.user)
        job = repo.get(validated_input["id"])
        return job.serialize()
