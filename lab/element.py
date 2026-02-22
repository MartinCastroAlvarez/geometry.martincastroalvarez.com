from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Generic, Iterator, TypeVar, overload

T = TypeVar("T")


class Element(ABC):
    def __str__(self) -> str:
        return self.__repr__()


class ComplexElement(Element):
    @abstractmethod
    def contains(self, obj: Element, inclusive: bool = True) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def overlaps(self, obj: Element, inclusive: bool = True) -> bool:
        raise NotImplementedError()


class Element1D(ComplexElement):
    @property
    @abstractmethod
    def size(self) -> Decimal:
        raise NotImplementedError()


class Element2D(ComplexElement):
    def __abs__(self) -> Decimal:
        return abs(self.signed_area)

    @property
    @abstractmethod
    def signed_area(self) -> Decimal:
        raise NotImplementedError()


class ElementSequence(ABC, Generic[T]):
    items: list[T]

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[T]:
        return iter(self.items)

    def contains(self, obj: T | ElementSequence[T]) -> bool:
        if isinstance(obj, ElementSequence):
            if len(obj) == 0:
                return True
            if len(obj) > len(self.items):
                return False
            i: int = self.index(obj.items[0])
            subsequence: ElementSequence[T] = self[i : i + len(obj)]
            return subsequence.items == obj.items
        return obj in self.items

    def __eq__(self, other: object) -> bool:
        other_items: list[T] | None = (
            getattr(other, "items", None)
            or getattr(other, "points", None)
            or getattr(other, "segments", None)
        )
        if other_items is None:
            return False
        n: int = len(self.items)
        if n != len(other_items):
            return False
        if n == 0:
            return True
        for start in range(n):
            if all(self.items[(start + j) % n] == other_items[j] for j in range(n)):
                return True
        return False

    def index(self, obj: T) -> int:
        return self.items.index(obj)

    @overload
    def __getitem__(self, key: int) -> T: ...  # noqa

    @overload
    def __getitem__(self, key: slice) -> ElementSequence[T]: ...  # noqa

    def __getitem__(self, key: int | slice) -> T | ElementSequence[T]:
        n: int = len(self.items)
        if n == 0 and isinstance(key, int):
            raise IndexError("sequence index out of range")
        if isinstance(key, slice):
            start: int = 0 if key.start is None else key.start
            stop: int = n if key.stop is None else key.stop
            if key.step not in (None, 1):
                raise ValueError("slicing only supports step=None or 1")
            s: int = start % n if n else 0
            e: int = stop % n if n else 0
            if s < e:
                return self.__class__(items=self.items[s:e])
            if s == e:
                return self.__class__(items=[])
            return self.__class__(items=self.items[s:] + self.items[:e])
        return self.items[key % n]

    def __invert__(self) -> ElementSequence[T]:
        return self.__class__(items=list(reversed(self.items)))

    def append(self, item: T) -> ElementSequence[T]:
        return self.__class__(items=self.items + [item])

    def insert(self, index: int, item: T) -> ElementSequence[T]:
        return self.__class__(items=self.items[:index] + [item] + self.items[index:])

    def pop(self, key: T | int) -> ElementSequence[T]:
        if isinstance(key, int):
            index: int = key % len(self.items)
        else:
            index = self.index(key)
        return self.__class__(items=self.items[:index] + self.items[index + 1 :])
