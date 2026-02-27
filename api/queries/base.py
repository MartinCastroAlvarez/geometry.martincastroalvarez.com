"""
Base query: validate, query, handle.

Title
-----
Query Base Classes

Context
-------
Query is the generic base: validate(body) -> T (request), query(T) -> R
(response), handle(body) = query(validate(body)). ListQuery validates
ListQueryRequest (next_token, limit). DetailsQuery validates DetailsQueryRequest
(id). For authenticated-only queries use PrivateQuery (queries.private).
Used by ArtGalleryListQuery, ArtGalleryDetailsQuery, JobListQuery, JobDetailsQuery.

Examples:
>>> query = ArtGalleryListQuery()
>>> result = query.handle(body={"next_token": "", "limit": 20})
"""

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from attributes import Identifier
from attributes import Limit
from attributes import Offset
from queries.request import DetailsQueryRequest
from queries.request import ListQueryRequest
from queries.request import QueryRequest
from queries.response import QueryResponse

T = TypeVar("T", bound=QueryRequest)
R = TypeVar("R", bound=QueryResponse)


class Query(Generic[T, R]):
    """
    Base query: validate, query, handle. No user; use PrivateQuery for auth.

    Example:
    >>> query = ArtGalleryListQuery()
    >>> query.handle(body={"next_token": "", "limit": 20})
    """

    def validate(self, body: dict[str, Any]) -> T:
        raise NotImplementedError

    def query(self, validated_input: T) -> R:
        raise NotImplementedError

    def handle(self, body: dict[str, Any]) -> R:
        validated_input = self.validate(body)
        return self.query(validated_input)


class ListQuery(Query[ListQueryRequest, R], Generic[R]):
    """Base for list queries. Validates ListQueryRequest (next_token, limit)."""

    def validate(self, body: dict[str, Any]) -> ListQueryRequest:
        return {
            "next_token": (Offset(body.get("next_token")) if body.get("next_token") is not None else None),
            "limit": (Limit(body.get("limit")) if body.get("limit") is not None else Limit(20)),
        }


class DetailsQuery(Query[DetailsQueryRequest, R], Generic[R]):
    """Base for details-by-id queries. Validates DetailsQueryRequest (id)."""

    def validate(self, body: dict[str, Any]) -> DetailsQueryRequest:
        return DetailsQueryRequest(id=Identifier(body.get("id")))
