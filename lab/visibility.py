from __future__ import annotations

from typing import Any, Generic, Iterator, TypeVar

from exceptions import GuardCoverageFailureError, VisibilityInvalidItemsError
from model import Hash
from point import Point
from serializable import Serializable

T = TypeVar("T", Hash, Point)


class Visibility(Generic[T], Serializable):
    def serialize(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in self.items.items():
            k = str(int(key))
            out[k] = [
                item.serialize() if isinstance(item, Point) else int(item)
                for item in value
            ]
        return out

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> Visibility[Point]:
        if not isinstance(data, dict):
            raise VisibilityInvalidItemsError(
                f"Visibility.unserialize expects a dict, got {type(data).__name__}"
            )
        items: dict[Hash, set[Point]] = {}
        for key, value in data.items():
            if not isinstance(value, list):
                raise VisibilityInvalidItemsError(
                    "Visibility.unserialize values must be lists"
                )
            items[Hash(key)] = {Point.unserialize(item) for item in value}
        return cls(items=items)

    def __init__(self, items: dict[Hash, set[T]] | None = None) -> None:
        self.items: dict[Hash, set[T]] = {} if items is None else items
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.items, dict):
            raise VisibilityInvalidItemsError(
                f"Visibility items must be a dictionary: {self.items!r}"
            )
        if not all(isinstance(key, Hash) for key in self.items.keys()):
            raise VisibilityInvalidItemsError(
                f"Visibility items must have Hash keys: {self.items!r}"
            )
        if not all(isinstance(value, set) for value in self.items.values()):
            raise VisibilityInvalidItemsError(
                f"Visibility items must have set values: {self.items!r}"
            )

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
