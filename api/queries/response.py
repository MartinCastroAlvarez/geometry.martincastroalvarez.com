"""
Query response: base TypedDict and reusable list/details response types.
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
