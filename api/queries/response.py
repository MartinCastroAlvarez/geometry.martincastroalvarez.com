"""
Query response: base TypedDict and reusable list/details response types.

Title
-----
Query Response Types

Context
-------
QueryResponse is the base. ListQueryResponse[T] has records: list[T] and
next_token: str. DetailsQueryResponse[R] is generic over the entity dict
type (e.g. JobDict, ArtGalleryDict). List handlers return {"records": [...], "next_token": ...};
details handlers return the serialized entity. Used for typing and
documentation of API response shape.

Examples:
>>> ListQueryResponse[ArtGalleryDict]
>>> DetailsQueryResponse[JobDict]
"""

from __future__ import annotations

from typing import Generic
from typing import TypedDict
from typing import TypeVar


class QueryResponse(TypedDict):
    """Base for query responses."""

    pass


R = TypeVar("R", bound=QueryResponse)
T = TypeVar("T")


class ListQueryResponse(QueryResponse, Generic[T]):
    """Generic list response: records and next_token. T is the entity dict type (e.g. JobDict, ArtGalleryDict)."""

    records: list[T]
    next_token: str


class DetailsQueryResponse(QueryResponse, Generic[R]):
    """Generic details response; R is the entity dict type (e.g. JobDict, ArtGalleryDict)."""

    pass
