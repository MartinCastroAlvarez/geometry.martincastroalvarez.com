"""
Base mutation: validate, mutate, handle.

Title
-----
Mutation Base Class

Context
-------
Mutation is the abstract base for write operations. It is generic over
request (T) and response (R) types. validate(body) returns validated
input T; mutate(validated_input) returns response R; handle(body) runs
validate then mutate. Subclasses implement validate and mutate. For
authenticated mutations use PrivateMutation (in mutations.private) which
checks user and passes user to the handler. Used by JobMutation,
JobUpdateMutation, ArtGalleryPublishMutation, ArtGalleryHideMutation.

Examples:
>>> class MyMutation(Mutation[MyRequest, MyResponse]):
>>> def validate(self, body): ...
>>> def mutate(self, validated_input): ...
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
