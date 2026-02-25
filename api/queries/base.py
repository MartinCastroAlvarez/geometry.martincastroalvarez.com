"""
Base query: validate, query, handle.
"""

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from queries.request import QueryRequest
from queries.response import QueryResponse

I = TypeVar("I", bound=QueryRequest)
O = TypeVar("O", bound=QueryResponse)


class Query(Generic[I, O]):
    """
    Base query: validate, query, handle. No user; use PrivateQuery for auth.

    Example:
    >>> query = ArtGalleryListQuery()
    >>> query.handle(body={"next_token": "", "limit": 20})
    """

    def __init__(self, **kwargs: Any) -> None:
        pass

    def validate(self, body: dict[str, Any]) -> I:
        raise NotImplementedError

    def query(self, validated_input: I) -> O:
        raise NotImplementedError

    def handle(self, body: dict[str, Any]) -> O:
        validated_input = self.validate(body)
        return self.query(validated_input)
