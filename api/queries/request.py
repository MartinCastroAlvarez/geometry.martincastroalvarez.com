"""
Query request: base TypedDict and reusable list/details request types.
"""

from __future__ import annotations

from typing import TypedDict

from attributes import Identifier
from attributes import Limit
from attributes import Offset


class QueryRequest(TypedDict):
    """Base for query requests."""

    pass


class ListQueryRequest(QueryRequest):
    """Request for list queries: next_token and limit."""

    next_token: Offset | None
    limit: Limit


class DetailsQueryRequest(QueryRequest):
    """Request for details-by-id queries."""

    id: Identifier
