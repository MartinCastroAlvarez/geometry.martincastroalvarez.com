"""
Query handlers for art galleries and jobs.

Title
-----
Queries Module

Context
-------
This module exports read-side handlers: ArtGalleryListQuery, ArtGalleryDetailsQuery,
JobListQuery, JobDetailsQuery. List queries use indexes (ArtGalleryPublicIndex,
JobsPrivateIndex) and return data + next_token. Details queries use
repositories and require id (from path). Job queries use PrivateControllerMixin
with ListQuery/DetailsQuery (user must be authenticated); gallery list/details
are public. Registered in api.api (ROUTES). All return dicts that the interceptor
JSON-serializes.

Examples:
>>> from queries import ArtGalleryListQuery, JobDetailsQuery
>>> query = ArtGalleryListQuery()
>>> result = query.handler(body={"limit": 20})
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from attributes import Identifier
from attributes import Limit
from attributes import Offset
from controllers import Controller
from controllers import ControllerRequest
from controllers import ControllerResponse
from controllers import PrivateControllerMixin
from indexes import ArtGalleryPublicIndex
from indexes import JobsPrivateIndex
from repositories import ArtGalleryRepository
from repositories import JobsRepository
from serializers import Serialized
from settings import DEFAULT_LIMIT


class QueryRequest(ControllerRequest):
    """Base for query requests."""

    pass


class ListQueryRequest(QueryRequest):
    """Request for list queries: next_token and limit."""

    next_token: Offset | None
    limit: Limit


class DetailsQueryRequest(QueryRequest):
    """Request for details-by-id queries."""

    id: Identifier


class QueryResponse(ControllerResponse):
    """Base for query responses."""

    pass


class ListQueryResponse(QueryResponse):
    """List response: data (list of Serialized) and next_token."""

    data: list[Serialized]
    next_token: str


class DetailsQueryResponse(QueryResponse):
    """Details response: data (single Serialized entity)."""

    data: Serialized


class Query(Controller):
    """
    Base query: validate, execute, handler. No user; use PrivateControllerMixin for auth.
    Subclasses implement validate() and query(); execute() delegates to query().

    For example, to run a list query:
    >>> query = ArtGalleryListQuery()
    >>> result = query.handler(body={"limit": 20})
    >>> "data" in result
    True
    """

    @abstractmethod
    def validate(self, body: dict[str, Any]) -> QueryRequest:
        pass

    def query(self, validated_input: QueryRequest) -> QueryResponse:
        """Subclasses override this; execute() delegates here."""
        raise NotImplementedError

    def execute(self, validated_input: QueryRequest) -> QueryResponse:
        """Delegate to query() for backward compatibility."""
        return self.query(validated_input)


class ListQuery(Query):
    """
    Base for list queries. Validates ListQueryRequest (next_token, limit).

    For example, to validate list params:
    >>> req = ListQuery().validate({"limit": 10})
    >>> req["limit"]
    Limit(10)
    """

    def validate(self, body: dict[str, Any]) -> ListQueryRequest:
        return {
            "next_token": (Offset(body.get("next_token")) if body.get("next_token") is not None else None),
            "limit": (Limit(body.get("limit")) if body.get("limit") is not None else Limit(DEFAULT_LIMIT)),
        }


class DetailsQuery(Query):
    """
    Base for details-by-id queries. Validates DetailsQueryRequest (id).

    For example, to get a single gallery by id:
    >>> query = ArtGalleryDetailsQuery()
    >>> result = query.handler(body={"id": "g1"})
    """

    def validate(self, body: dict[str, Any]) -> DetailsQueryRequest:
        return DetailsQueryRequest(id=Identifier(body.get("id")))


class ArtGalleryListQuery(ListQuery):
    """
    List galleries using the public index. Public query; no user check.

    For example, to list galleries with pagination:
    >>> query = ArtGalleryListQuery()
    >>> result = query.handler({"limit": 20, "next_token": ""})
    >>> result["data"][0]["id"]
    '...'
    """

    def query(self, validated_input: ListQueryRequest) -> ListQueryResponse:
        index = ArtGalleryPublicIndex()
        records, next_token = index.search(
            next_token=validated_input.get("next_token"),
            limit=validated_input["limit"],
        )
        return {
            "data": [record.serialize() for record in records],
            "next_token": str(next_token) if next_token else "",
        }


class ArtGalleryDetailsQuery(DetailsQuery):
    """
    Get a single gallery by id from the repository. Public query; no user check.

    For example, to get gallery details:
    >>> query = ArtGalleryDetailsQuery()
    >>> result = query.handler({"id": "gallery-123"})
    >>> result["data"]["boundary"]
    [...]
    """

    def query(self, validated_input: DetailsQueryRequest) -> DetailsQueryResponse:
        repo = ArtGalleryRepository()
        gallery = repo.get(validated_input["id"])
        return {"data": gallery.serialize()}


class JobListQuery(PrivateControllerMixin, ListQuery):
    """
    List jobs for the current user using the private index.

    For example, to list the authenticated user's jobs:
    >>> query = JobListQuery(user=request.user)
    >>> result = query.handler({"limit": 20})
    """

    def query(self, validated_input: ListQueryRequest) -> ListQueryResponse:
        index = JobsPrivateIndex(user_email=self.user.email)
        records, next_token = index.search(
            next_token=validated_input.get("next_token"),
            limit=validated_input["limit"],
        )
        return {
            "data": [record.serialize() for record in records],
            "next_token": str(next_token) if next_token else "",
        }


class JobDetailsQuery(PrivateControllerMixin, DetailsQuery):
    """
    Get a single job by id (must be owner).

    For example, to get job details for the current user:
    >>> query = JobDetailsQuery(user=request.user)
    >>> result = query.handler({"id": "job-123"})
    >>> result["data"]["id"]
    'job-123'
    """

    def query(self, validated_input: DetailsQueryRequest) -> DetailsQueryResponse:
        repo = JobsRepository(user=self.user)
        job = repo.get(validated_input["id"])
        return {"data": job.serialize()}
