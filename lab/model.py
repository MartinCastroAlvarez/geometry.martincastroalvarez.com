from __future__ import annotations

import hashlib
from abc import ABC
from typing import Any, Generic, Iterator, TypeVar
from uuid import uuid4

from exceptions import (HashInvalidValueError, ModelMapInvalidDataError,
                        ModelMapKeyError)


class Hash(int):
    def __new__(cls, value: Any) -> Hash:
        if value is None:
            raise HashInvalidValueError("Hash value must not be None")
        if not isinstance(value, str):
            value = str(value)
        if len(value) == 0:
            raise HashInvalidValueError("Hash value must be non-empty")
        raw: bytes = value.encode()
        hashed: bytes = hashlib.sha256(raw).digest()[:8]
        int_value: int = int.from_bytes(hashed, "big")
        return super().__new__(cls, int_value)

    def __hash__(self) -> int:
        return int(self)


class Model(ABC):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.id: Hash = Hash(uuid4())

    def __hash__(self) -> int:
        return int(self.id)

    def __str__(self) -> str:
        return self.__repr__()


T = TypeVar("T", bound=Model)


class ModelMap(Generic[T]):
    def __init__(
        self,
        *,
        items: dict[Hash, T] | list[T] | None = None,
    ) -> None:
        if items is None:
            self.items: dict[Hash, T] = {}
        elif isinstance(items, dict):
            self.items = items
        elif isinstance(items, list):
            for item in items:
                if not isinstance(item, Model):
                    raise ModelMapInvalidDataError(
                        f"items list must contain Model instances, got {type(item).__name__}"
                    )
            self.items = {item.id: item for item in items}
        else:
            raise ModelMapInvalidDataError(
                f"items must be a dict, list, or None, got {type(items).__name__}"
            )

    def __getitem__(self, key: Hash) -> T:
        if key not in self.items:
            raise ModelMapKeyError(f"key not in ModelMap: {key}")
        return self.items[key]

    def __setitem__(self, key: Hash, value: T) -> None:
        self.items[key] = value

    def __iadd__(self, item: T) -> ModelMap[T]:
        self.items[item.id] = item
        return self

    def __iter__(self) -> Iterator[T]:  # type: ignore[override]
        return iter(self.items.values())

    def keys(self) -> Iterator[Hash]:
        return iter(self.items.keys())

    def values(self) -> Iterator[T]:
        return iter(self.items.values())

    def entries(self) -> Iterator[tuple[Hash, T]]:
        return iter(self.items.items())

    def __len__(self) -> int:
        return len(self.items)

    def add(self, item: T) -> None:
        self.items[item.id] = item

    def pop(self, key: Hash) -> None:
        if key not in self.items:
            raise ModelMapKeyError(f"key not in ModelMap: {key}")
        del self.items[key]

    def clone(self) -> ModelMap[T]:
        return ModelMap(items=dict(self.items))
