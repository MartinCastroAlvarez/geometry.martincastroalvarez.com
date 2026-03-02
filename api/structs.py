"""
Data structures: Sequence[T], Table[T], Bag[K,T].

Title
-----
Structs Module

Context
-------
This module provides reusable data structures. Sequence[T] is a list-like
with modular slicing (wrap-around), shift, add/sub/and/invert, and
canonical hash; used by Polygon and geometry. Table[T] is a dict-like
keyed by hash(item), with add/pop and Serializable[dict]; used for
obstacles, ears, convex_components, guards, visibility in ArtGallery.
Bag[K,T] is a key plus set of items (set-like: +=, -=, __iter__, __len__, __contains__).
Use Table[Bag[K,T]] for a table of bags. Both support serialize/unserialize for S3 and API.

Examples:
>>> from structs import Sequence, Table, Bag
>>> seq = Sequence([p0, p1, p2])
>>> seq[1:4]  # wrap-around slice
Sequence([p1, p2, p0])
>>> table = Table().add(ear1).add(ear2)
>>> table[ear1] is ear1
True
>>> bag = Bag("key")
>>> bag += 1
>>> bag += 2
>>> len(bag)
2
>>> table.add(bag)
>>> len(table)
3
"""

from __future__ import annotations

import json
from typing import Any
from typing import Generic
from typing import Iterator
from typing import TypeVar

from attributes import Signature
from exceptions import SequenceMultipleOverlapsError
from exceptions import ValidationError
from interfaces import Serializable

K = TypeVar("K")
T = TypeVar("T")


class Sequence(list, Generic[T]):
    """
    List-like sequence with modular slicing (wrap-around), shift, add/sub/and/invert, hash, serialize.

    Context
    -------
    Used by Polygon and geometry for cyclic vertex/edge lists. Slicing wraps (mod len).
    Shift puts an index or element first/last. Add/sub/and support concatenation, removal of
    contiguous subsequence, and intersection; hash is canonical by rotation.

    Slicing: indices wrap (mod len). s[3:6] on length-4 sequence gives s[3:4] + s[0:2].
    Shift: s << idx or s << element puts that index/element first; >> puts it last.
    Add: s + other concatenates. Sub: s - other removes first contiguous occurrence of other (with wrap).
    And: s & other returns the contiguous subsequence that appears in both (with wrap); raises if multiple overlaps.
    Invert: ~s returns reversed copy.
    Hash: idempotent by canonical rotation (same value for same cycle regardless of start).

    Examples
    --------
    >>> from structs import Sequence
    >>> seq = Sequence([p0, p1, p2, p3])
    >>> seq[2:5]  # wrap-around slice
    Sequence([p2, p3, p0])
    >>> seq << 2  # rotate so index 2 is first
    Sequence([p2, p3, p0, p1])
    >>> seq + Sequence([p4])  # concatenate
    Sequence([p0, p1, p2, p3, p4])
    """

    def __init__(
        self,
        value: list[T] | None = None,
    ) -> None:
        """
        Build a Sequence from an iterable; deduplicates contiguous and wrap duplicates in place.

        Context
        -------
        None or non-list iterables are converted to a list; then dedup() is applied so that
        consecutive duplicates and first-equals-last are removed.

        Examples
        --------
        >>> from structs import Sequence
        >>> Sequence([1, 1, 2, 2, 1])
        Sequence([1, 2, 1])
        >>> Sequence([a, b, a])
        Sequence([a, b])
        """
        if value is None:
            value = []
        if not isinstance(value, list):
            value = list(value) if value is not None else []
        super().__init__(value)
        self.dedup()

    def __getitem__(self, key: int | slice) -> T | Sequence[T]:
        """
        Single element by index (mod len), or slice with wrap-around (step must be None or 1).

        Context
        -------
        Enables cyclic access: seq[i] and seq[i:j] where indices wrap so that
        seq[1:4] on a length-3 sequence yields seq[1:3] + seq[0:1].

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2])
        >>> seq[1]
        p1
        >>> seq[1:4]  # wrap-around slice
        Sequence([p1, p2, p0])
        """
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
                return Sequence(list(self)[s:e])
            if s == e:
                return Sequence([])
            return Sequence(list(self)[s:] + list(self)[:e])
        return super().__getitem__(key % n)

    def __lshift__(self, other: int | T) -> Sequence[T]:
        """
        Rotate so index n or element other becomes first.

        Context
        -------
        Returns a new Sequence with the same cycle but starting at the given index or element;
        used to normalize polygon start vertex.

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2])
        >>> seq << 1
        Sequence([p1, p2, p0])
        >>> seq << p2
        Sequence([p2, p0, p1])
        """
        if not self:
            return Sequence([])
        n = len(self)
        if isinstance(other, int):
            i = other % n
        else:
            i = self.index(other)
        return Sequence(list(self)[i:] + list(self)[:i])

    def __rshift__(self, other: int | T) -> Sequence[T]:
        """
        Rotate so index n or element other becomes last (i.e. index n+1 becomes first).

        Context
        -------
        Inverse of __lshift__ in the sense that (seq >> k) puts the element at k at the end.

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2])
        >>> seq >> 0
        Sequence([p1, p2, p0])
        >>> seq >> p1
        Sequence([p2, p0, p1])
        """
        if not self:
            return Sequence([])
        n = len(self)
        if isinstance(other, int):
            i = (other + 1) % n
        else:
            i = (self.index(other) + 1) % n
        return Sequence(list(self)[i:] + list(self)[:i])

    def __add__(self, other: Sequence[T]) -> Sequence[T]:
        """
        Concatenate with other (no boundary merge).

        Context
        -------
        Returns a new Sequence; does not deduplicate at the join. Use for building
        longer cycles from two sequences.

        Examples
        --------
        >>> from structs import Sequence
        >>> Sequence([p0, p1]) + Sequence([p2, p3])
        Sequence([p0, p1, p2, p3])
        """
        if not isinstance(other, Sequence):
            return NotImplemented
        return Sequence(list(self) + list(other))

    def __iadd__(self, other: Sequence[T]) -> Sequence[T]:
        """
        In-place concatenation with another Sequence.

        Context
        -------
        Extends self with other and returns self; no dedup at the boundary.

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1])
        >>> seq += Sequence([p2])
        >>> seq
        Sequence([p0, p1, p2])
        """
        if not isinstance(other, Sequence):
            return NotImplemented
        self.extend(other)
        return self

    def __sub__(self, other: Sequence[T]) -> Sequence[T]:
        """
        Remove first occurrence of other as contiguous subsequence (with wrap). Return new sequence.

        Context
        -------
        Scans cyclically for a contiguous match to other; if found, returns the remainder
        as a new Sequence. If not found or other is empty, returns a copy of self.

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2, p3])
        >>> seq - Sequence([p2, p3])
        Sequence([p0, p1])
        >>> seq - Sequence([p3, p0])  # wrap
        Sequence([p1, p2])
        """
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
        """
        In-place: remove first occurrence of other as contiguous subsequence (with wrap).

        Context
        -------
        Same as __sub__ but mutates self and returns self; used when trimming a cycle in place.

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2])
        >>> seq -= Sequence([p1])
        >>> seq
        Sequence([p0, p2])
        """
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

        Context
        -------
        Used to find the common contiguous arc when comparing two cyclic sequences
        (e.g. polygon boundaries); exactly one overlap is required.

        Examples
        --------
        >>> from structs import Sequence
        >>> Sequence([p0, p1, p2]) & Sequence([p1, p2, p3])
        Sequence([p1, p2])
        >>> Sequence([p0, p1]) & Sequence([p2, p3])
        Sequence([])
        """
        if not isinstance(other, Sequence):
            return NotImplemented
        n: int = len(self)
        m: int = len(other)
        if n == 0 or m == 0:
            return Sequence([])

        shared: Sequence[T] = Sequence([])
        i: int = 0
        while i < n:
            if self[i] not in other:
                i += 1
                continue
            if len(shared):
                raise SequenceMultipleOverlapsError("Sequences overlap in multiple places")
            # Extend shared with the longest contiguous slice from self starting at i that appears in other
            max_len: int = 0
            for length in range(1, min(n, m) + 1):
                slice_self: Sequence[T] = self[i : i + length]
                in_other: bool = False
                for start_other in range(m):
                    slice_other = other[start_other : start_other + length]
                    if slice_self == slice_other:
                        in_other = True
                        break
                if not in_other:
                    break
                max_len = length
            shared.extend(self[i + j] for j in range(max_len))
            i += max_len
        return shared

    def __invert__(self) -> Sequence[T]:
        """
        Reversed copy of the sequence.

        Context
        -------
        Returns a new Sequence with opposite orientation; used for canonical hash
        (forward vs backward cycle).

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2])
        >>> ~seq
        Sequence([p2, p1, p0])
        """
        return Sequence(list(reversed(self)))

    def __hash__(self) -> Signature:
        """
        Idempotent hash: same value for the same sequence regardless of start point or orientation.

        Context
        -------
        Canonicalizes by rotating to the minimum element and choosing the lexicographically
        smaller of forward and reversed; enables set/dict keying of cycles.

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2])
        >>> hash(seq) == hash(seq << 1)
        True
        >>> hash(seq) == hash(~seq)
        True
        """
        if not self:
            return Signature("sequence:empty")
        minimum: T = min(self)
        forward: Sequence[T] = Sequence(self)
        backward: Sequence[T] = Sequence(reversed(self))
        idx_forward: int = forward.index(minimum)
        idx_backward: int = backward.index(minimum)
        forward_shifted: Sequence[T] = forward << idx_forward
        backward_shifted: Sequence[T] = backward << idx_backward
        key_forward: tuple[T, ...] = tuple(forward_shifted)
        key_backward: tuple[T, ...] = tuple(backward_shifted)
        canonical: tuple[T, ...] = min((key_forward, key_backward), key=lambda t: (t[-1], t))
        return Signature(canonical)

    def __contains__(self, obj: object) -> bool:
        """
        Element in self, or (when obj is Sequence) contiguous subsequence in self with wrap.

        Context
        -------
        Single elements use list membership; Sequence arguments check for a contiguous
        (wrapping) occurrence of that subsequence.

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2])
        >>> p1 in seq
        True
        >>> Sequence([p2, p0]) in seq  # wrap
        True
        """
        if isinstance(obj, Sequence):
            if len(obj) == 0:
                return True
            if len(obj) > len(self):
                return False
            try:
                i = self.index(obj[0])
            except ValueError:
                return False
            k = len(obj)
            return self[i : i + k] == obj
        return list.__contains__(self, obj)

    def __len__(self) -> int:
        """
        Number of elements in the sequence.

        Context
        -------
        Same as list length; used for wrap-around index arithmetic.

        Examples
        --------
        >>> from structs import Sequence
        >>> len(Sequence([p0, p1, p2]))
        3
        """
        return list.__len__(self)

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over elements in order.

        Context
        -------
        Yields items from index 0 to len(self)-1; same as list iteration.

        Examples
        --------
        >>> from structs import Sequence
        >>> list(Sequence([p0, p1, p2]))
        [p0, p1, p2]
        """
        return list.__iter__(self)

    def index(self, obj: T) -> int:
        """
        Index of first occurrence of obj. Raises ValueError if not found.

        Context
        -------
        Same as list.index; indices are in range [0, len(self)).

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2])
        >>> seq.index(p1)
        1
        """
        return list.index(self, obj)

    def append(self, item: T) -> Sequence[T]:
        """
        Append item in place and return self.

        Context
        -------
        Mutates the sequence; returned self allows chaining (e.g. seq.append(a).append(b)).

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0]).append(p1).append(p2)
        >>> seq
        Sequence([p0, p1, p2])
        """
        list.append(self, item)
        return self

    def insert(self, index: int, item: T) -> Sequence[T]:
        """
        Insert item at index in place and return self.

        Context
        -------
        Same semantics as list.insert; index is not modulo length (no wrap).

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p2]).insert(1, p1)
        >>> seq
        Sequence([p0, p1, p2])
        """
        list.insert(self, index, item)
        return self

    def pop(self, key: int | T = -1) -> T:
        """
        Remove and return item at index, or at index of key if key is an element.

        Context
        -------
        key can be an int (default -1 for last) or an element; if element, uses index()
        and pops at that position.

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1, p2])
        >>> seq.pop(-1)
        p2
        >>> seq.pop(p1)
        p1
        """
        if isinstance(key, int):
            return list.pop(self, key)
        idx = self.index(key)
        return list.pop(self, idx)

    def dedup(self) -> Sequence[T]:
        """
        In-place: remove contiguous duplicates and wrap duplicate (first equals last).
        Do not remove non-consecutive duplicates; a sequence can pass through the same point multiple times.
        Returns self.

        Context
        -------
        Used in __init__ and when normalizing polygons so that consecutive repeated vertices
        and redundant last-equals-first are removed.

        Examples
        --------
        >>> from structs import Sequence
        >>> Sequence([1, 1, 2, 2, 1]).dedup()
        Sequence([1, 2, 1])
        >>> Sequence([a, b, a]).dedup()
        Sequence([a, b])
        """
        if not self:
            return self
        result: list[T] = [self[0]]
        for i in range(1, len(self)):
            if self[i] != self[i - 1]:
                result.append(self[i])
        while len(result) >= 2 and result[0] == result[-1]:
            result.pop()
        self.clear()
        self.extend(result)
        return self

    def serialize(self) -> list[Any]:
        """
        Export to list; Serializable elements call serialize(), others use hash(item).

        Context
        -------
        Produces a JSON-friendly list for API/S3; each item is serialized per Serializable
        or by hash for non-Serializable elements.

        Examples
        --------
        >>> from structs import Sequence
        >>> seq = Sequence([p0, p1])
        >>> seq.serialize()
        [p0.serialize(), p1.serialize()]
        """
        out: list[Any] = []
        for item in self:
            val = item.serialize() if isinstance(item, Serializable) else hash(item)
            out.append(json.loads(val) if isinstance(val, str) else val)
        return out

    @classmethod
    def unserialize(cls, data: Any) -> Sequence[T]:
        """
        Build a Sequence from a list of already-unserialized items.

        Context
        -------
        Single argument only: data is a list. Caller is responsible for unserializing
        each element (e.g. Polygon.unserialize for each item) before passing.

        Examples
        --------
        >>> from structs import Sequence
        >>> Sequence.unserialize([p0, p1, p2])
        Sequence([p0, p1, p2])
        """
        if not isinstance(data, list):
            data = []
        return cls(data)


class Table(dict[int, Any], Generic[T], Serializable[dict[str, Any]]):
    """
    Dict-like collection where key is hash(item). Items must be hashable.
    Add with add(item) or table += item; remove with pop(key) or table -= item_or_key.

    Context
    -------
    Used for obstacles, ears, convex_components, guards, visibility in ArtGallery.
    Key is always hash(item); lookup by key (int) or by item. Supports serialize/unserialize for S3 and API.

    Examples
    --------
    >>> from structs import Table
    >>> table = Table().add(poly1).add(poly2)
    >>> len(table)
    2
    >>> table[poly1] is poly1
    True
    >>> table -= poly1
    >>> len(table)
    1
    """

    def add(self, item: T) -> Table[T]:
        """
        Add item; key is hash(item). Returns self for chaining.

        Context
        -------
        Stores item under hash(item); overwrites if the same hash was already present.
        Chainable for building tables in one expression.

        Examples
        --------
        >>> from structs import Table
        >>> table = Table().add(ear1).add(ear2)
        >>> table[ear1] is ear1
        True
        """
        self[hash(item)] = item
        return self

    def __iadd__(self, item: T) -> Table[T]:
        """
        Add item; key is hash(item).

        Context
        -------
        Same as add(item); allows table += item syntax.

        Examples
        --------
        >>> from structs import Table
        >>> table = Table()
        >>> table += item
        >>> item in table
        True
        """
        self.add(item)
        return self

    def __isub__(self, item_or_key: T | int) -> Table[T]:
        """
        Remove by key (int) or by item (then key = hash(item)).

        Context
        -------
        In-place removal; if item_or_key is int and in self, that key is deleted;
        otherwise key is hash(item_or_key).

        Examples
        --------
        >>> from structs import Table
        >>> table = Table().add(a).add(b)
        >>> table -= a
        >>> a in table
        False
        >>> table -= hash(b)
        >>> len(table)
        0
        """
        key: int = item_or_key if isinstance(item_or_key, int) and item_or_key in self else hash(item_or_key)
        del self[key]
        return self

    def __contains__(self, item_or_key: object) -> bool:
        """
        True if the key (int) or the item (value) is in the table.

        Context
        -------
        int: membership by key. Other: membership by value (key must match hash(item_or_key)).

        Examples
        --------
        >>> from structs import Table
        >>> table = Table().add(item)
        >>> item in table
        True
        >>> hash(item) in table
        True
        """
        if isinstance(item_or_key, int):
            return dict.__contains__(self, item_or_key)
        key = hash(item_or_key)
        return key in self and self[key] == item_or_key

    def __getitem__(self, key_or_item: int | T) -> T:
        """
        Look up by key (int) or by item (then key = hash(item)).

        Context
        -------
        If key_or_item is int and in self, returns the value; else uses hash(key_or_item).
        Raises KeyError if not found.

        Examples
        --------
        >>> from structs import Table
        >>> table = Table().add(ear1).add(ear2)
        >>> table[ear1] is ear1
        True
        >>> table[hash(ear2)] is ear2
        True
        """
        if isinstance(key_or_item, int) and key_or_item in self:
            return dict.__getitem__(self, key_or_item)
        k = hash(key_or_item)
        if k in self:
            return dict.__getitem__(self, k)
        raise KeyError(key_or_item)

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over values (items).

        Context
        -------
        Yields each stored item; order is dict iteration order (insertion order in Python 3.7+).

        Examples
        --------
        >>> from structs import Table
        >>> table = Table().add(a).add(b)
        >>> list(table)
        [a, b]
        """
        return iter(self.values())

    def __hash__(self) -> Signature:
        """
        Signature of the concatenation of sorted hash() of the items (deterministic).

        Context
        -------
        Used for canonical fingerprinting of the table contents regardless of insertion order.

        Examples
        --------
        >>> from structs import Table
        >>> t1 = Table().add(a).add(b)
        >>> t2 = Table().add(b).add(a)
        >>> hash(t1) == hash(t2)
        True
        """
        part = "_".join(str(hash(item)) for item in sorted(self.values(), key=hash))
        return Signature(part)

    def __or__(self, other: Table[T]) -> Table[T]:
        """
        Merge two tables; result has all items from self and other. Same key (hash): other wins.

        Context
        -------
        Returns a new Table; does not mutate self or other. Useful for combining guards, components, etc.

        Examples
        --------
        >>> from structs import Table
        >>> t1 = Table().add(a); t2 = Table().add(b)
        >>> merged = t1 | t2
        >>> len(merged)
        2
        >>> a in merged and b in merged
        True
        """
        if not isinstance(other, Table):
            return NotImplemented
        result: Table[T] = Table()
        result.update(self)
        result.update(other)
        return result

    def serialize(self) -> dict[str, Any]:
        """
        Return dict mapping str(hash(item)) -> serialize(item); Serializable uses serialize(), else hash.

        Context
        -------
        Produces JSON-friendly dict for API/S3; each value is item.serialize() or hash(item).

        Examples
        --------
        >>> from structs import Table
        >>> table = Table().add(poly1).add(poly2)
        >>> table.serialize()
        {str(hash(poly1)): poly1.serialize(), str(hash(poly2)): poly2.serialize()}
        """
        return {str(hash(item)): (item.serialize() if isinstance(item, Serializable) else hash(item)) for item in self.values()}

    @classmethod
    def unserialize(cls, data: Any) -> Table[T]:
        """
        Build a Table from a list of items or dict of key -> item (already unserialized).
        List: each item added with key hash(item). Dict: key must equal hash(value) or raise.

        Context
        -------
        Caller must pass already-unserialized items. Dict form is used when loading from API/S3
        wire format where keys are string hashes.

        Examples
        --------
        >>> from structs import Table
        >>> Table.unserialize([a, b])
        Table(...)
        >>> Table.unserialize({str(hash(a)): a, str(hash(b)): b})
        Table(...)
        """
        result: Table[T] = cls()
        if isinstance(data, list):
            for item in data:
                result[hash(item)] = item
        elif isinstance(data, dict):
            for key, value in data.items():
                k = int(key)
                if hash(value) != k:
                    raise ValidationError("Table key does not match hash of item")
                result[k] = value
        return result


class Bag(Generic[K, T], Serializable[list[Any]]):
    """
    A key (e.g. component or guard) and a set of items. Set-like over the items: +=, -=, __iter__, __len__, __contains__.
    __hash__ is the key's hash so Table[Bag] keys match the key type's table.

    Context
    -------
    Use Table[Bag[K,T]] for a table of bags keyed by K. Items are stored in a set; no duplicates.
    Supports serialize/unserialize for S3 and API (sorted by hash).

    Examples
    --------
    >>> from structs import Bag, Table
    >>> bag = Bag("key")
    >>> bag += 1
    >>> bag += 2
    >>> len(bag)
    2
    >>> 1 in bag
    True
    >>> bag -= 1
    >>> len(bag)
    1
    >>> bag.serialize()
    [2]
    >>> table = Table().add(bag)
    >>> len(table)
    1
    """

    def __init__(self, key: K) -> None:
        """
        Create an empty bag with the given key.

        Context
        -------
        The key identifies the bag (e.g. component id, guard id); hash(bag) == hash(key)
        so that Table[Bag] lookup works by key.

        Examples
        --------
        >>> from structs import Bag
        >>> bag = Bag("guard_1")
        >>> len(bag)
        0
        >>> hash(bag) == hash("guard_1")
        True
        """
        self.key: K = key
        self.items: set[T] = set()

    def __hash__(self) -> int:
        """
        Hash of the bag's key (so Table[Bag] keys match the key type).

        Context
        -------
        Two bags with the same key hash equal; used for Table lookup and deduplication.

        Examples
        --------
        >>> from structs import Bag
        >>> hash(Bag("k")) == hash("k")
        True
        """
        return hash(self.key)

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over the items in the bag.

        Context
        -------
        Yields each item in the set (order is arbitrary).

        Examples
        --------
        >>> from structs import Bag
        >>> bag = Bag("k"); bag += 1; bag += 2
        >>> set(bag)
        {1, 2}
        """
        return iter(self.items)

    def __len__(self) -> int:
        """
        Number of items in the bag.

        Context
        -------
        Same as len(bag.items); duplicate adds do not increase length.

        Examples
        --------
        >>> from structs import Bag
        >>> bag = Bag("k"); bag += 1; bag += 2
        >>> len(bag)
        2
        """
        return len(self.items)

    def __contains__(self, item: object) -> bool:
        """
        True if item is in the bag.

        Context
        -------
        Set membership; used for "item in bag" checks.

        Examples
        --------
        >>> from structs import Bag
        >>> bag = Bag("k"); bag += 1
        >>> 1 in bag
        True
        >>> 2 in bag
        False
        """
        return item in self.items

    def __and__(self, other: Bag[K, T]) -> set[T]:
        """
        Return the intersection of this bag's items and the other bag's items.

        Context
        -------
        Enables ``bag1 & bag2`` to test whether two bags share any items; the result
        is a set, so ``bool(bag1 & bag2)`` is True when the intersection is non-empty.

        Examples
        --------
        >>> from structs import Bag
        >>> a = Bag("x"); a += 1; a += 2
        >>> b = Bag("y"); b += 2; b += 3
        >>> a & b
        {2}
        >>> bool(a & b)
        True
        """
        if not isinstance(other, Bag):
            return NotImplemented
        return self.items & other.items

    def __iadd__(self, other: T) -> Bag[K, T]:
        """
        Add an item. No-op if already present.

        Context
        -------
        Items are stored in a set; duplicate adds have no effect. Returns self for chaining.

        Examples
        --------
        >>> from structs import Bag
        >>> bag = Bag("k")
        >>> bag += 1
        >>> bag += 1
        >>> len(bag)
        1
        """
        self.items.add(other)
        return self

    def __isub__(self, other: T) -> Bag[K, T]:
        """
        Remove an item. No-op if not present.

        Context
        -------
        Uses set.discard so missing items do not raise. Returns self.

        Examples
        --------
        >>> from structs import Bag
        >>> bag = Bag("k"); bag += 1; bag += 2
        >>> bag -= 1
        >>> 1 in bag
        False
        >>> bag -= 99
        >>> len(bag)
        1
        """
        self.items.discard(other)
        return self

    def serialize(self) -> list[Any]:
        """
        Return sorted list: Serializable items call serialize(), others use hash(item).

        Context
        -------
        Items are sorted by hash for deterministic output; used for API/S3. Table[Bag[K,T]].serialize()
        gives dict key id -> list of item ids.

        Examples
        --------
        >>> from structs import Bag
        >>> bag = Bag("key"); bag += 1; bag += 2
        >>> bag.serialize()
        [1, 2]
        """
        return [item.serialize() if isinstance(item, Serializable) else hash(item) for item in sorted(self.items, key=hash)]

    @classmethod
    def unserialize(cls, data: Any) -> Bag[K, T]:
        """
        Base implementation: key must be supplied by subclass. Override in subclasses (e.g. from_serialized(key, data)).

        Context
        -------
        Bag.unserialize does not have a key in the wire format; subclasses that need to
        reconstruct from (key, data) should override and call Bag(key) then += items.

        Examples
        --------
        Subclasses override: e.g. Component.from_serialized(key, data) builds Bag(key)
        and extends it with unserialized items from data.
        """
        raise NotImplementedError("Bag.unserialize requires key; use Bag(key) and += items")
