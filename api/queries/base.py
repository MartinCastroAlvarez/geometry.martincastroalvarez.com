"""
Base query: validate, query, handle.
"""

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar
from typing import TypedDict

from models import User

T = TypeVar("T", bound="QueryInput")


class QueryInput(TypedDict):
    """Base TypedDict for query inputs."""

    pass


class Query(Generic[T]):
    """
    Base query: validate, query, handle. Subclasses implement validate and query.

    Example:
    >>> query = ArtGalleryListQuery(user=user)
    >>> query.handle(body={"next_token": "", "limit": 20})
    """

    def __init__(self, user: User) -> None:
        self.user = user

    def validate(self, body: dict[str, Any] | None = None) -> T:
        raise NotImplementedError

    def query(self, validated_input: T) -> dict[str, Any]:
        raise NotImplementedError

    def handle(self, body: dict[str, Any] | None = None) -> dict[str, Any]:
        validated_input = self.validate(body)
        return self.query(validated_input)
