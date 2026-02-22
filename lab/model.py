from __future__ import annotations

import hashlib
from abc import ABC
from typing import Any, Generic, Iterator, TypeVar
from uuid import UUID, uuid4

from exceptions import ModelMapInvalidDataError, ModelMapKeyError


class Model(ABC):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.id = uuid4()

    def __hash__(self) -> int:
        return int.from_bytes(hashlib.sha256(self.id.bytes).digest()[:8], "big")

    def __str__(self) -> str:
        return self.__repr__()


T = TypeVar("T", bound=Model)


class ModelMap(Generic[T]):
    def __init__(
        self,
        *,
        items: dict[UUID, T] | list[T] | None = None,
    ) -> None:
        if items is None:
            self.data: dict[UUID, T] = {}
        elif isinstance(items, dict):
            self.data = items
        elif isinstance(items, list):
            for item in items:
                if not isinstance(item, Model):
                    raise ModelMapInvalidDataError(
                        f"items list must contain Model instances, got {type(item).__name__}"
                    )
            self.data = {item.id: item for item in items}
        else:
            raise ModelMapInvalidDataError(
                f"items must be a dict, list, or None, got {type(items).__name__}"
            )

    def __getitem__(self, key: UUID) -> T:
        if key not in self.data:
            raise ModelMapKeyError(f"key not in ModelMap: {key}")
        return self.data[key]

    def __setitem__(self, key: UUID, value: T) -> None:
        self.data[key] = value

    def __iadd__(self, item: T) -> ModelMap[T]:
        self.data[item.id] = item
        return self

    def __iter__(self) -> Iterator[T]:  # type: ignore[override]
        return iter(self.data.values())

    def keys(self) -> Iterator[UUID]:
        return iter(self.data.keys())

    def values(self) -> Iterator[T]:
        return iter(self.data.values())

    def items(self) -> Iterator[tuple[UUID, T]]:
        return iter(self.data.items())

    def __len__(self) -> int:
        return len(self.data)

    def add(self, item: T) -> None:
        self.data[item.id] = item

    def pop(self, key: UUID) -> None:
        if key not in self.data:
            raise ModelMapKeyError(f"key not in ModelMap: {key}")
        del self.data[key]

    def clone(self) -> ModelMap[T]:
        return ModelMap(items=dict(self.data))
