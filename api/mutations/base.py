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

I = TypeVar("I", bound=MutationRequest)
O = TypeVar("O", bound=MutationResponse)


class Mutation(ABC, Generic[I, O]):
    """Base mutation: validate, mutate, handle. No user; use PrivateMutation for auth."""

    def __init__(self, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def validate(self, body: dict[str, Any]) -> I:
        pass

    @abstractmethod
    def mutate(self, validated_input: I) -> O:
        pass

    def handle(self, body: dict[str, Any]) -> O:
        validated_input = self.validate(body)
        return self.mutate(validated_input)
