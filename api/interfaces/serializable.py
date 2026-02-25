"""
Abstract base for types that can be serialized to and from a wire/storage type T.

Model (api/models/) and Indexed (api/index/indexed.py) implement Serializable[dict] for
S3 persistence and JSON transport. Geometry types may implement Serializable[list] or
Serializable[str]. Subclasses must implement serialize() and unserialize().
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

T = TypeVar("T")


class Serializable(ABC, Generic[T]):
    """
    Abstract base for objects that support serialize() and unserialize() with type T.

    Example (dict):
    >>> data = my_model.serialize()
    >>> obj = MyModel.unserialize(data)

    Example (list):
    >>> data = polygon.serialize()
    >>> obj = Polygon.unserialize(data)

    Example (str, Point):
    >>> s = point.serialize()
    >>> obj = Point.unserialize(s)
    """

    @abstractmethod
    def serialize(self) -> T:
        """
        Return the serialized representation of this object (dict, list, str, etc.).
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def unserialize(cls, data: T) -> Serializable[T]:
        """
        Build an instance from serialized data. Always returns an instance of Serializable.
        """
        raise NotImplementedError
