"""
Base mutation: validate, mutate, handle.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import TypedDict

from models import User

T = TypeVar("T", bound="MutationInput")


class MutationInput(TypedDict):
    """Base for mutation inputs."""

    pass


class Mutation(ABC, Generic[T]):
    """Base mutation requiring an authenticated user."""

    def __init__(self, user: User) -> None:
        self.user = user

    @abstractmethod
    def validate(self, body: dict[str, Any] | None = None) -> T:
        pass

    @abstractmethod
    def mutate(self, validated_input: T) -> dict[str, Any]:
        pass

    def handle(self, body: dict[str, Any] | None = None) -> dict[str, Any]:
        validated_input = self.validate(body)
        return self.mutate(validated_input)
