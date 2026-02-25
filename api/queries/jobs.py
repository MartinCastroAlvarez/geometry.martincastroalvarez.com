"""
Job list and job details queries.
"""

from __future__ import annotations

from indexes.jobs import JobsPrivateIndex
from models.job import JobDict
from queries.base import DetailsQuery
from queries.base import ListQuery
from queries.private import PrivateQuery
from queries.request import DetailsQueryRequest
from queries.request import ListQueryRequest
from queries.response import DetailsQueryResponse
from queries.response import ListQueryResponse
from repositories.jobs import JobsRepository


class JobListQuery(
    PrivateQuery[ListQueryRequest, ListQueryResponse[JobDict]],
    ListQuery[ListQueryResponse[JobDict]],
):
    """List jobs for the current user using the private index."""

    def query(self, validated_input: ListQueryRequest) -> ListQueryResponse[JobDict]:
        index = JobsPrivateIndex(user_email=self.user.email)
        records, next_token = index.search(
            next_token=validated_input.get("next_token"),
            limit=validated_input["limit"],
        )
        return {
            "records": [record.serialize() for record in records],
            "next_token": str(next_token) if next_token else "",
        }


class JobDetailsQuery(
    PrivateQuery[DetailsQueryRequest, DetailsQueryResponse[JobDict]],
    DetailsQuery[DetailsQueryResponse[JobDict]],
):
    """Get a single job by id (must be owner)."""

    def query(self, validated_input: DetailsQueryRequest) -> DetailsQueryResponse[JobDict]:
        repo = JobsRepository(user=self.user)
        job = repo.get(validated_input["id"])
        return job.serialize()
