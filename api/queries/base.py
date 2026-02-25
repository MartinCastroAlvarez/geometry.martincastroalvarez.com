"""
Base query: validate, query, handle.
"""

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from models import User

from queries.request import QueryRequest
from queries.response import QueryResponse

I = TypeVar("I", bound=QueryRequest)
O = TypeVar("O", bound=QueryResponse)


class Query(Generic[I, O]):
    """
    Base query: validate, query, handle. Subclasses implement validate and query.

    Example:
    >>> query = ArtGalleryListQuery(user=user)
    >>> query.handle(body={"next_token": "", "limit": 20})
    """

    def __init__(self, user: User) -> None:
        self.user = user

    def validate(self, body: dict[str, Any] | None = None) -> I:
        raise NotImplementedError

    def query(self, validated_input: I) -> O:
        raise NotImplementedError

    def handle(self, body: dict[str, Any] | None = None) -> O:
        payload: dict[str, Any] = body if body is not None else {}
        validated_input = self.validate(payload)
        return self.query(validated_input)
