"""
Job list query.
"""

from __future__ import annotations

from typing import Any

from attributes import Limit
from attributes import Offset
from indexes.jobs import JobsPrivateIndex
from models.job import JobDict

from queries.private import PrivateQuery
from queries.request import ListQueryRequest
from queries.response import ListQueryResponse


class JobListQueryResponse(ListQueryResponse):
    """List response with job records."""

    records: list[JobDict]


class JobListQuery(PrivateQuery[ListQueryRequest, JobListQueryResponse]):
    """List jobs for the current user using the private index."""

    def _validate_body(self, body: dict[str, Any]) -> ListQueryRequest:
        return {
            "next_token": Offset(body.get("next_token")) if body.get("next_token") is not None else None,
            "limit": Limit(body.get("limit")) if body.get("limit") is not None else Limit(20),
        }

    def query(self, validated_input: ListQueryRequest) -> JobListQueryResponse:
        index = JobsPrivateIndex(user_email=self.user.email)
        limit = validated_input["limit"]
        records, next_token = index.search(
            next_token=validated_input.get("next_token"),
            limit=limit,
        )
        return {
            "records": [record.serialize() for record in records],
            "next_token": str(next_token) if next_token else "",
        }
