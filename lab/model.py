from __future__ import annotations

import hashlib
from abc import ABC
from typing import Any, Generic, Iterator, TypeVar
from uuid import uuid4

from exceptions import (HashInvalidValueError, ModelMapInvalidDataError,
                        ModelMapKeyError)
from serializable import Serializable


class Hash(int):
    def __new__(cls, value: Any) -> Hash:
        if value is None:
            raise HashInvalidValueError("Hash value must not be None")
        if not isinstance(value, str):
            value = str(value)
        if len(value) == 0:
            raise HashInvalidValueError("Hash value must be non-empty")
        raw: bytes = value.encode()
        hashed: bytes = hashlib.sha256(raw).digest()[:16]
        int_value: int = int.from_bytes(hashed, "big")
        return super().__new__(cls, int_value)

    def __hash__(self) -> Hash:
        return self


class Model(ABC):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.id: Hash = Hash(uuid4())

    def __hash__(self) -> Hash:
        return self.id

    def __str__(self) -> str:
        return self.__repr__()


T = TypeVar("T", bound=Model)


class ModelMap(Generic[T], Serializable):
    def serialize(self) -> dict[int, dict[str, Any]]:
        return {int(key): item.serialize() for key, item in self.items.items()}

    @classmethod
    def unserialize(
        cls,
        data: dict[str, Any] | list[Any],
        item_class: type[T],
    ) -> ModelMap[T]:
        if data is None:
            data = []
        if isinstance(data, dict):
            if "items" in data:
                raw_list = data["items"]
                if not isinstance(raw_list, list):
                    raise ModelMapInvalidDataError(
                        "ModelMap.unserialize 'items' must be a list"
                    )
                items_list: list[T] = []
                for item in raw_list:
                    if isinstance(item, Model):
                        items_list.append(item)
                    else:
                        items_list.append(item_class.unserialize(item))
                return cls(items=items_list)
            # dict key -> payload; key must equal instance.id after deserialization
            result: dict[Hash, T] = {}
            for key, val in data.items():
                instance = item_class.unserialize(val)
                key_int = int(key) if not isinstance(key, Hash) else int(key)
                if int(instance.id) != key_int:
                    raise ModelMapInvalidDataError(
                        f"ModelMap key {key!r} does not match item id {instance.id!r}"
                    )
                result[instance.id] = instance
            return cls(items=result)
        if isinstance(data, list):
            items_list = []
            for item in data:
                if isinstance(item, Model):
                    items_list.append(item)
                else:
                    items_list.append(item_class.unserialize(item))
            return cls(items=items_list)
        raise ModelMapInvalidDataError(
            f"ModelMap.unserialize expects a dict or list, got {type(data).__name__}"
        )

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

    def __hash__(self) -> Hash:
        sorted_ids: list[Hash] = sorted(self.items.keys())
        return Hash(":".join(str(key) for key in sorted_ids))
