"""
Job list and job details queries.

Title
-----
Job Queries

Context
-------
JobListQuery lists jobs for the current user via JobsPrivateIndex;
returns records and next_token. JobDetailsQuery loads a single job by
id from JobsRepository(user); user must own the job. Both require
authentication (PrivateControllerMixin). Used for GET v1/jobs (list) and GET v1/jobs/:id
(details). Handler receives request.user from the private decorator.

Examples:
>>> GET v1/jobs?limit=20&next_token=... -> JobListQuery
>>> GET v1/jobs/:id -> JobDetailsQuery
"""

from __future__ import annotations

from controllers import PrivateControllerMixin
from indexes.jobs import JobsPrivateIndex
from queries.base import DetailsQuery
from queries.base import ListQuery
from queries.request import DetailsQueryRequest
from queries.request import ListQueryRequest
from queries.response import ListQueryResponse
from repositories import JobsRepository
from serializers import Serialized


class JobListQuery(PrivateControllerMixin, ListQuery):
    """List jobs for the current user using the private index."""

    def query(self, validated_input: ListQueryRequest) -> ListQueryResponse:
        index = JobsPrivateIndex(user_email=self.user.email)
        records, next_token = index.search(
            next_token=validated_input.get("next_token"),
            limit=validated_input["limit"],
        )
        return {
            "records": [record.serialize() for record in records],
            "next_token": str(next_token) if next_token else "",
        }


class JobDetailsQuery(PrivateControllerMixin, DetailsQuery):
    """Get a single job by id (must be owner)."""

    def query(self, validated_input: DetailsQueryRequest) -> Serialized:
        repo = JobsRepository(user=self.user)
        job = repo.get(validated_input["id"])
        return job.serialize()
