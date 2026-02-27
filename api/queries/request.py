"""
Query request: base TypedDict and reusable list/details request types.

Title
-----
Query Request Types

Context
-------
QueryRequest is the base TypedDict. ListQueryRequest has next_token
(Offset | None) and limit (Limit). DetailsQueryRequest has id (Identifier).
List queries get next_token and limit from body (merged with path params);
details queries get id from path. Used by Query.validate() return types
and by ListQuery/DetailsQuery base implementations.

Examples:
>>> ListQueryRequest(next_token=Offset(...), limit=Limit(20))
>>> DetailsQueryRequest(id=Identifier("gallery-123"))
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
