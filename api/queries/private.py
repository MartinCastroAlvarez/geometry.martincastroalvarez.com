"""
Private query: request type with user_email; base class that requires authenticated user.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from attributes import Email
from exceptions import UnauthorizedError
from models import User

from queries.base import Query
from queries.request import QueryRequest
from queries.response import QueryResponse

I = TypeVar("I", bound=QueryRequest)
O = TypeVar("O", bound=QueryResponse)


class PrivateQueryRequest(QueryRequest):
    """Request shape for private queries: base request + user_email."""

    user_email: Email


class PrivateQuery(Query[I, O], Generic[I, O]):
    """Query that requires an authenticated user. Sets self.user; validate checks user then _validate_body."""

    def __init__(self, *, user: User, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.user = user

    def validate(self, body: dict[str, Any]) -> I:
        if self.user is None or not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        return self._validate_body(body)

    @abstractmethod
    def _validate_body(self, body: dict[str, Any]) -> I:
        """Parse and validate body; called after user check."""
        ...
