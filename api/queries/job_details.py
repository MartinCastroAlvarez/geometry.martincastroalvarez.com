"""
Job details query.
"""

from __future__ import annotations

from typing import Any

from exceptions import UnauthorizedError
from repositories.jobs import JobsRepository
from attributes import Identifier

from queries.base import Query
from queries.request import QueryRequest
from queries.response import QueryResponse


class JobDetailsQueryRequest(QueryRequest):
    """Request for job by id."""

    id: Identifier


class JobDetailsQueryResponse(QueryResponse):
    """Response for job details: single job dict."""

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


class JobDetailsQuery(Query[JobDetailsQueryRequest, JobDetailsQueryResponse]):
    """Get a single job by id (must be owner)."""

    def validate(self, body: dict[str, Any] | None = None) -> JobDetailsQueryRequest:
        if not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        payload = body or {}
        return JobDetailsQueryRequest(id=Identifier(payload.get("id")))

    def query(self, validated_input: JobDetailsQueryRequest) -> JobDetailsQueryResponse:
        repo = JobsRepository(user=self.user)
        job = repo.get(validated_input["id"])
        return job.serialize()
