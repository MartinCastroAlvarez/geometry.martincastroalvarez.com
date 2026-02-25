"""
Base mutation: validate, mutate, handle.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from mutations.request import MutationRequest
from mutations.response import MutationResponse

T = TypeVar("T", bound=MutationRequest)
R = TypeVar("R", bound=MutationResponse)


class Mutation(ABC, Generic[T, R]):
    """Base mutation: validate, mutate, handle. No user; use PrivateMutation for auth."""

    @abstractmethod
    def validate(self, body: dict[str, Any]) -> T:
        pass

    @abstractmethod
    def mutate(self, validated_input: T) -> R:
        pass

    def handle(self, body: dict[str, Any]) -> R:
        validated_input = self.validate(body)
        return self.mutate(validated_input)
