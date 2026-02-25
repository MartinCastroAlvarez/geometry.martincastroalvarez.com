"""
Abstract base for types that can be serialized to and from JSON-compatible dicts.

Model (api/models/) and Indexed (api/index/indexed.py) implement this interface for
S3 persistence and JSON transport. Subclasses must implement to_dict() and from_dict().
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class Serializable(ABC):
    """
    Abstract base for objects that support to_dict and from_dict.

    Example:
    >>> data = my_model.to_dict()
    >>> obj = MyModel.from_dict(data)
    """

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Return a JSON-compatible dict representation of this object.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> Serializable:
        """
        Build an instance from a dict (e.g. loaded from storage).
        """
        raise NotImplementedError
