"""
Generic Sequence[T] type: list with optional None (-> []), slicing, shift, hash, add/sub/__and__/invert, in-place, serialize/unserialize.
"""

from __future__ import annotations

import json
from typing import Any
from typing import Callable
from typing import Generic
from typing import Iterator
from typing import overload
from typing import TypeVar

from exceptions import SequenceMultipleOverlapsError

from attributes.signature import Signature

T = TypeVar("T")


class Sequence(list, Generic[T]):
    """
    A list-like sequence: slicing (modular), __lshift__/__rshift__, __add__/__sub__/__and__/__invert__,
    __iadd__/__isub__, index(), append(), insert(), pop(), dedup(), __contains__ (element or subsequence), __hash__.
    """

    def __init__(
        self,
        value: list[T] | None = None,
    ) -> None:
        if value is None:
            value = []
        if not isinstance(value, list):
            value = list(value) if value is not None else []
        super().__init__(value)

    @overload
    def __getitem__(self, key: int) -> T: ...

    @overload
    def __getitem__(self, key: slice) -> Sequence[T]: ...

    def __getitem__(self, key: int | slice) -> T | Sequence[T]:
        n: int = len(self)
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
                return Sequence(self[s:e])
            if s == e:
                return Sequence([])
            return Sequence(self[s:] + self[:e])
        return super().__getitem__(key % n)

    def __lshift__(self, other: int | T) -> Sequence[T]:
        """Rotate so index n or element other becomes first."""
        if not self:
            return Sequence([])
        n = len(self)
        if isinstance(other, int):
            i = other % n
        else:
            i = self.index(other)
        return Sequence(list(self)[i:] + list(self)[:i])

    def __rshift__(self, other: int | T) -> Sequence[T]:
        """Rotate so index n or element other becomes last (index n+1 first)."""
        if not self:
            return Sequence([])
        n = len(self)
        if isinstance(other, int):
            i = (other + 1) % n
        else:
            i = (self.index(other) + 1) % n
        return Sequence(list(self)[i:] + list(self)[:i])

    def __add__(self, other: Sequence[T]) -> Sequence[T]:
        """Concatenate with other (no boundary merge)."""
        if not isinstance(other, Sequence):
            return NotImplemented
        return Sequence(list(self) + list(other))

    def __iadd__(self, other: Sequence[T]) -> Sequence[T]:
        """In-place concatenation."""
        if not isinstance(other, Sequence):
            return NotImplemented
        self.extend(other)
        return self

    def __sub__(self, other: Sequence[T]) -> Sequence[T]:
        """Remove first occurrence of other as contiguous subsequence (with wrap). Return new sequence."""
        n = len(self)
        k = len(other)
        if n == 0 or k == 0:
            return Sequence(list(self))
        lst = list(self)
        for start in range(n):
            if all(lst[(start + j) % n] == other[j] for j in range(k)):
                if k == n:
                    return Sequence([])
                remainder = [lst[((start + k) % n + j) % n] for j in range(n - k)]
                return Sequence(remainder)
        return Sequence(list(self))

    def __isub__(self, other: Sequence[T]) -> Sequence[T]:
        """In-place: remove first occurrence of other as contiguous subsequence (with wrap)."""
        n = len(self)
        k = len(other)
        if n == 0 or k == 0:
            return self
        for start in range(n):
            if all(self[(start + j) % n] == other[j] for j in range(k)):
                if k == n:
                    self.clear()
                    return self
                remainder = [self[((start + k) % n + j) % n] for j in range(n - k)]
                self.clear()
                self.extend(remainder)
                return self
        return self

    def __and__(self, other: Sequence[T]) -> Sequence[T]:
        """
        Return the contiguous subsequence that appears in both (with wrap).
        If nothing matches, return empty Sequence. If multiple disjoint overlaps, raise SequenceMultipleOverlapsError.
        """
        if not isinstance(other, Sequence):
            return NotImplemented
        n = len(self)
        m = len(other)
        if n == 0 or m == 0:
            return Sequence([])

        def slice_in_other(slice_self: list[T], length: int) -> bool:
            for start_other in range(m):
                slice_other = [other[(start_other + j) % m] for j in range(length)]
                if slice_self == slice_other:
                    return True
            return False

        # All contiguous runs that appear in both
        all_runs: list[tuple[T, ...]] = []
        for start_self in range(n):
            for length in range(1, min(n, m) + 1):
                slice_self = [self[(start_self + j) % n] for j in range(length)]
                if slice_in_other(slice_self, length):
                    all_runs.append(tuple(slice_self))

        # Keep only runs not contained in any other (maximal by containment)
        def contained(tup: tuple[T, ...], in_run: tuple[T, ...]) -> bool:
            if len(tup) >= len(in_run):
                return False
            for i in range(len(in_run) - len(tup) + 1):
                if in_run[i : i + len(tup)] == tup:
                    return True
            return False

        maximal_runs: list[tuple[T, ...]] = []
        for run in all_runs:
            if not any(contained(run, other_run) for other_run in all_runs if other_run != run):
                if run not in maximal_runs:
                    maximal_runs.append(run)

        if len(maximal_runs) == 0:
            return Sequence([])
        if len(maximal_runs) > 1:
            raise SequenceMultipleOverlapsError(
                "Sequences overlap in multiple places"
            )
        return Sequence(list(maximal_runs[0]))

    def __invert__(self) -> Sequence[T]:
        """Reversed copy."""
        return Sequence(list(reversed(self)))

    def __hash__(self) -> Signature:
        """
        Idempotent hash: same value for the same sequence regardless of start point or orientation.
        """
        if not self:
            return Signature("sequence:empty")
        min_el = min(self)
        forward = Sequence(self)
        backward = Sequence(reversed(self))
        idx_forward = forward.index(min_el)
        idx_backward = backward.index(min_el)
        forward_shifted = forward << idx_forward
        backward_shifted = backward << idx_backward
        key_forward = tuple(forward_shifted)
        key_backward = tuple(backward_shifted)
        canonical = min((key_forward, key_backward), key=lambda t: (t[-1], t))
        return Signature(canonical)

    def __contains__(self, obj: object) -> bool:
        """Element in self, or (when obj is Sequence) contiguous subsequence in self with wrap."""
        if isinstance(obj, Sequence):
            if len(obj) == 0:
                return True
            if len(obj) > len(self):
                return False
            try:
                i = self.index(obj[0])
            except ValueError:
                return False
            n, k = len(self), len(obj)
            return all(self[(i + j) % n] == obj[j] for j in range(k))
        return list.__contains__(self, obj)

    def __len__(self) -> int:
        return list.__len__(self)

    def __iter__(self) -> Iterator[T]:
        return list.__iter__(self)

    def index(self, obj: T) -> int:
        """Index of first occurrence of obj. Raises ValueError if not found."""
        return list.index(self, obj)

    def append(self, item: T) -> Sequence[T]:
        """Append in place and return self."""
        list.append(self, item)
        return self

    def insert(self, index: int, item: T) -> Sequence[T]:
        """Insert in place and return self."""
        list.insert(self, index, item)
        return self

    def pop(self, key: int | T = -1) -> T:
        """Remove and return item at index, or at index of key if key is an element."""
        if isinstance(key, int):
            return list.pop(self, key)
        idx = self.index(key)
        return list.pop(self, idx)

    def dedup(self) -> Sequence[T]:
        """Return a new sequence with consecutive duplicates removed (preserves order)."""
        if not self:
            return Sequence([])
        result: list[T] = [self[0]]
        for i in range(1, len(self)):
            if self[i] != self[i - 1]:
                result.append(self[i])
        return Sequence(result)

    def serialize(self) -> list[Any]:
        """Export to list; elements must support serialize() or be serializable."""
        out: list[Any] = []
        for item in self:
            if hasattr(item, "serialize") and callable(getattr(item, "serialize")):
                val = item.serialize()
                out.append(json.loads(val) if isinstance(val, str) else val)
            else:
                out.append(item)
        return out

    @classmethod
    def unserialize(
        cls,
        data: list[Any],
        item_from: Callable[[Any], T],
    ) -> Sequence[T]:
        """Build Sequence from list using item_from for each element."""
        if not isinstance(data, list):
            data = []
        return cls([item_from(x) for x in data])
