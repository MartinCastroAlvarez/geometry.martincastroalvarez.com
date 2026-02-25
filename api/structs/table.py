"""
Table: dict-like collection keyed by hash(item). Add with add/+=, remove with pop/-=.
Serializable[dict]: serialize to dict key -> item.serialize(); unserialize from list of items or dict (key must match hash(item)).
"""

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import Iterator
from typing import TypeVar

from attributes.signature import Signature
from exceptions import ValidationError
from interfaces import Serializable

T = TypeVar("T")


class Table(dict[int, Any], Generic[T], Serializable[dict[str, Any]]):
    """
    Dict-like collection where key is hash(item). Items must be hashable.
    Add with add(item) or table += item; remove with pop(key) or table -= item_or_key.
    """

    def add(self, item: T) -> Table[T]:
        """Add item; key is hash(item). Returns self for chaining."""
        self[hash(item)] = item
        return self

    def __iadd__(self, item: T) -> Table[T]:
        """Add item; key is hash(item)."""
        self.add(item)
        return self

    def __isub__(self, item_or_key: T | int) -> Table[T]:
        """Remove by key (int) or by item (then key = hash(item))."""
        key: int = item_or_key if item_or_key in self else hash(item_or_key)
        del self[key]
        return self

    def __contains__(self, item_or_key: object) -> bool:
        """True if the key (int) or the item (value) is in the table."""
        if isinstance(item_or_key, int):
            return dict.__contains__(self, item_or_key)
        key = hash(item_or_key)
        return key in self and self[key] == item_or_key

    def __iter__(self) -> Iterator[T]:
        """Iterate over values (items)."""
        return iter(self.values())

    def __hash__(self) -> Signature:
        """Signature of the concatenation of sorted hash() of the items (deterministic)."""
        part = "_".join(str(hash(item)) for item in sorted(self.values(), key=hash))
        return Signature(part)

    def __or__(self, other: Table[T]) -> Table[T]:
        """Merge two tables; result has all items from self and other. Same key (hash): other wins."""
        if not isinstance(other, Table):
            return NotImplemented
        result: Table[T] = Table()
        result.update(self)
        result.update(other)
        return result

    def serialize(self) -> dict[str, Any]:
        """Return dict mapping str(hash(item)) -> item.serialize()."""
        return {str(hash(item)): item.serialize() for item in self.values()}

    @classmethod
    def unserialize(cls, data: Any) -> Table[T]:
        """
        Single argument only: data is a list of items or dict of key -> item to put in the table.
        Caller must pass already-unserialized items (e.g. gallery.py calls Polygon.unserialize,
        Ear.unserialize, ConvexComponent.unserialize, Point.unserialize before calling this).
        List: each item added with key hash(item). Dict: key must equal hash(value) or raise.
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
