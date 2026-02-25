"""
Base mutation: validate, mutate, handle.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from models import User

from mutations.request import MutationRequest
from mutations.response import MutationResponse

I = TypeVar("I", bound=MutationRequest)
O = TypeVar("O", bound=MutationResponse)


class Mutation(ABC, Generic[I, O]):
    """Base mutation requiring an authenticated user."""

    def __init__(self, user: User) -> None:
        self.user = user

    @abstractmethod
    def validate(self, body: dict[str, Any] | None = None) -> I:
        pass

    @abstractmethod
    def mutate(self, validated_input: I) -> O:
        pass

    def handle(self, body: dict[str, Any] | None = None) -> O:
        payload: dict[str, Any] = body if body is not None else {}
        validated_input = self.validate(payload)
        return self.mutate(validated_input)
