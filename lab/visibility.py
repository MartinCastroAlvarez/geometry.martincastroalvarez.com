from __future__ import annotations

from typing import Generic, Iterator, TypeVar

from exceptions import GuardCoverageFailureError, VisibilityInvalidItemsError
from model import Hash
from point import Point

T = TypeVar("T", Hash, Point)


class Visibility(Generic[T]):
    def __init__(self, items: dict[Hash, set[T]] | None = None) -> None:
        self.items: dict[Hash, set[T]] = {}
        if items is not None:
            if not isinstance(items, dict):
                raise VisibilityInvalidItemsError(
                    f"Visibility items must be a dictionary: {items!r}"
                )
            if not all(isinstance(key, Hash) for key in items.keys()):
                raise VisibilityInvalidItemsError(
                    f"Visibility items must have Hash keys: {items!r}"
                )
            if not all(isinstance(value, set) for value in items.values()):
                raise VisibilityInvalidItemsError(
                    f"Visibility items must have set values: {items!r}"
                )
            self.items = items

    def __setitem__(self, key: Hash, value: set[T]) -> None:
        self.items[key] = value

    def __getitem__(self, key: Hash) -> set[T]:
        return self.items[key]

    def keys(self) -> Iterator[Hash]:
        return self.items.keys()

    def values(self) -> Iterator[set[T]]:
        return self.items.values()

    def sees(self, value: T) -> set[Hash]:
        return {key for key in self.items.keys() if value in self.items[key]}

    @property
    def best(self) -> list[Hash]:
        keys: list[Hash] = list(self.items.keys())
        if not keys:
            raise GuardCoverageFailureError("No guard can see any remaining component.")
        coverage: dict[Hash, int] = {key: len(self.items[key]) for key in keys}
        max_coverage: int = max(coverage.values())
        winners: list[Hash] = [key for key in keys if coverage[key] == max_coverage]
        if not winners:
            raise GuardCoverageFailureError("No guard can see any remaining component.")
        return winners
