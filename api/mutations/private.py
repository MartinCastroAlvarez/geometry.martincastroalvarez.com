"""
Private mutation: base class that requires authenticated user.
"""

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from exceptions import UnauthorizedError
from models import User
from mutations.base import Mutation
from mutations.request import MutationRequest
from mutations.response import MutationResponse

T = TypeVar("T", bound=MutationRequest)
R = TypeVar("R", bound=MutationResponse)


class PrivateMutation(Mutation[T, R], Generic[T, R]):

    def __init__(self, *, user: User, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.user = user

    def validate(self, body: dict[str, Any]) -> T:
        if self.user is None or not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        return super().validate(body)
