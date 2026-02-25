"""
Index entry: index_id (sort key) and real_id (record id).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from attributes import Identifier
from exceptions import ValidationError
from interfaces import Serializable


@dataclass
class Indexed(Serializable):
    """
    Stored index entry: index_id (sort key) and real_id (actual record id).

    Example:
    >>> entry = Indexed(index_id="123", real_id="gal_abc")
    >>> data = entry.to_dict()
    >>> entry = Indexed.from_dict(data)
    """

    index_id: Identifier
    real_id: Identifier

    def to_dict(self) -> dict[str, Any]:
        return {"index_id": str(self.index_id), "real_id": str(self.real_id)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Indexed:
        if not isinstance(data, dict):
            raise ValidationError("Indexed data must be a dict")
        return cls(
            index_id=Identifier(data.get("index_id")),
            real_id=Identifier(data.get("real_id")),
        )
