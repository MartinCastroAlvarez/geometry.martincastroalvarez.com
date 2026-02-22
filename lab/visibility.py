from __future__ import annotations

from typing import Any, Generic, TypeVar
from uuid import UUID

from exceptions import GuardCoverageFailureError
from point import Point

T = TypeVar("T", UUID, Point)


class Visibility(Generic[T]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.data: dict[UUID, set[T]] = {}

    def __setitem__(self, key: UUID, value: set[T]) -> None:
        self.data[key] = value

    def __getitem__(self, key: UUID) -> set[T]:
        return self.data[key]

    def sees(self, value: T) -> set[T]:
        return {key for key in self.data.keys() if value in self.data[key]}

    @property
    def best(self) -> UUID:
        uuid_keys: list[UUID] = list(self.data.keys())
        if not uuid_keys:
            raise GuardCoverageFailureError("No guard can see any remaining component.")
        best_key: UUID = max(
            uuid_keys,
            key=lambda k: (len(self.data[k]), -k.int),
        )
        if len(self.data[best_key]) == 0:
            raise GuardCoverageFailureError("No guard can see any remaining component.")
        return best_key
