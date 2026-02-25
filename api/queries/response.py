"""
Query response: base TypedDict and reusable list/details response types.
"""

from __future__ import annotations

from typing import Any
from typing import TypedDict


class QueryResponse(TypedDict):
    """Base for query responses."""

    pass


class ListQueryResponse(QueryResponse):
    """Response for list queries: records and next_token."""

    records: list[dict[str, Any]]
    next_token: str


class DetailsQueryResponse(QueryResponse):
    """Base for details responses; entity-specific subclasses add fields."""

    pass
