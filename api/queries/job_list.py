"""
Job list query.
"""

from __future__ import annotations

from typing import Any

from attributes import Limit
from exceptions import UnauthorizedError
from index.jobs import JobsPrivateIndex

from queries.base import Query
from queries.request import QueryRequest
from queries.response import QueryResponse


class JobListQueryRequest(QueryRequest, total=False):
    """Request for listing jobs (requires authenticated user)."""

    next_token: str
    limit: Limit


class JobListQueryResponse(QueryResponse):
    """Response for job list: records and next_token."""

    records: list[dict[str, Any]]
    next_token: str


class JobListQuery(Query[JobListQueryRequest, JobListQueryResponse]):
    """List jobs for the current user using the private index."""

    def validate(self, body: dict[str, Any] | None = None) -> JobListQueryRequest:
        if not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated to list jobs")
        payload = body or {}
        next_token = payload.get("next_token") or ""
        raw_limit = payload.get("limit")
        out: JobListQueryRequest = {"next_token": next_token}
        if raw_limit is not None:
            out["limit"] = Limit(raw_limit)
        return out

    def query(self, validated_input: JobListQueryRequest) -> JobListQueryResponse:
        email = self.user.email
        if email is None:
            raise UnauthorizedError("User must be authenticated to list jobs")
        index = JobsPrivateIndex(user_email=email)
        limit = validated_input.get("limit") or Limit(20)
        records, next_token = index.search(
            next_token=validated_input.get("next_token") or None,
            limit=limit,
        )
        return {
            "records": [record.serialize() for record in records],
            "next_token": next_token,
        }
