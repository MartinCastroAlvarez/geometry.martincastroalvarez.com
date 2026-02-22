from __future__ import annotations

from typing import Any, Generic, TypeVar

from exceptions import GuardCoverageFailureError
from model import Hash
from point import Point

T = TypeVar("T", Hash, Point)


class Visibility(Generic[T]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.items: dict[Hash, set[T]] = {}

    def __setitem__(self, key: Hash, value: set[T]) -> None:
        self.items[key] = value

    def __getitem__(self, key: Hash) -> set[T]:
        return self.items[key]

    def sees(self, value: T) -> set[Hash]:
        return {key for key in self.items.keys() if value in self.items[key]}

    @property
    def best(self) -> Hash:
        keys: list[Hash] = list(self.items.keys())
        if not keys:
            raise GuardCoverageFailureError("No guard can see any remaining component.")
        best: Hash = max(
            keys,
            key=lambda k: (len(self.items[k]), -k),
        )
        if len(self.items[best]) == 0:
            raise GuardCoverageFailureError("No guard can see any remaining component.")
        return best
