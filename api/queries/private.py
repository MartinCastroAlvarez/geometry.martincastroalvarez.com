"""
Private query: base class that requires authenticated user.
"""

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from exceptions import UnauthorizedError
from models import User
from queries.base import Query
from queries.request import QueryRequest
from queries.response import QueryResponse

T = TypeVar("T", bound=QueryRequest)
R = TypeVar("R", bound=QueryResponse)


class PrivateQuery(Query[T, R], Generic[T, R]):

    def __init__(self, *, user: User, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.user = user

    def validate(self, body: dict[str, Any]) -> T:
        if self.user is None or not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        return super().validate(body)
