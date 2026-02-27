"""
Private query: base class that requires authenticated user.

Title
-----
PrivateQuery Base Class

Context
-------
PrivateQuery extends Query and requires an authenticated user. Constructor
takes user: User. validate(body) first checks user is not None and
user.is_authenticated(); otherwise raises UnauthorizedError. Then calls
super().validate(body). Job list and details use PrivateQuery so only
the owning user can see their jobs. The API handler instantiates with
user=request.user for routes registered as PrivateQuery.

Examples:
>>> class JobListQuery(PrivateQuery[...], ListQuery[...]):
>>> def query(self, validated_input): ...
>>> handler = JobListQuery(user=request.user)
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
