"""
Index entry: index_id (sort key) and real_id (record id).

Title
-----
Indexed (Index Entry)

Context
-------
Indexed is the stored form of an index entry: index_id is the sort key
(e.g. Countdown as string for newest-first), real_id is the actual record
identifier. Serialized as dict with index_id and real_id strings. Used when
saving to an index (Index.save(Indexed(...))) and when loading from
search (Indexed.unserialize(data); repository.get(indexed.real_id)).
Identifier type is used for both fields.

Examples:
    entry = Indexed(index_id="123", real_id="gal_abc")
    data = entry.serialize()
    entry = Indexed.unserialize(data)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import TypedDict

from attributes import Identifier
from exceptions import ValidationError
from interfaces import Serializable


class IndexedDict(TypedDict):
    """Serialized form of Indexed (serialize/unserialize)."""

    index_id: str
    real_id: str


@dataclass
class Indexed(Serializable[dict[str, Any]]):
    """
    Stored index entry: index_id (sort key) and real_id (actual record id).

    Example:
    >>> entry = Indexed(index_id="123", real_id="gal_abc")
    >>> data = entry.serialize()
    >>> entry = Indexed.unserialize(data)
    """

    index_id: Identifier
    real_id: Identifier

    def serialize(self) -> IndexedDict:
        return {"index_id": str(self.index_id), "real_id": str(self.real_id)}

    @classmethod
    def unserialize(cls, data: Any) -> Indexed:
        if not isinstance(data, dict):
            raise ValidationError("Indexed data must be a dict")
        return cls(
            index_id=Identifier(data.get("index_id")),
            real_id=Identifier(data.get("real_id")),
        )
