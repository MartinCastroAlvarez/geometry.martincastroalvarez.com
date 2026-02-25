"""
Private mutation: request type with user_email; base class that requires authenticated user.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from attributes import Email
from exceptions import UnauthorizedError
from models import User

from mutations.base import Mutation
from mutations.request import MutationRequest
from mutations.response import MutationResponse

I = TypeVar("I", bound=MutationRequest)
O = TypeVar("O", bound=MutationResponse)


class PrivateMutationRequest(MutationRequest):
    """Request shape for private mutations: base request + user_email."""

    user_email: Email


class PrivateMutation(Mutation[I, O], Generic[I, O]):
    """Mutation that requires an authenticated user. Sets self.user; validate checks user then _validate_body."""

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
