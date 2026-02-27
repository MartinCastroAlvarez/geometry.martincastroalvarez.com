"""
Abstract base for types that can be serialized to and from a wire/storage type T.

Title
-----
Serializable Interface

Context
-------
Serializable[T] is the abstract base for types that can be converted to
and from a wire/storage representation T. Model and Indexed use
Serializable[dict] for S3 and JSON. Geometry types use Serializable[list]
or Serializable[str] (e.g. Point -> JSON array string). Subclasses must
implement serialize() -> T and classmethod unserialize(data) -> instance.
Validation and coercion belong in unserialize. Used everywhere data is
persisted or sent over the API.

Examples:
    data = my_model.serialize()
    obj = MyModel.unserialize(data)
    s = point.serialize()
    obj = Point.unserialize(s)
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
    def unserialize(cls, data: Any) -> Serializable[T]:
        """
        Build an instance from serialized data. Subclasses must validate and coerce data.
        Always returns an instance of Serializable.
        """
        raise NotImplementedError
