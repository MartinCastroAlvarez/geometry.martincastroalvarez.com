"""
API interfaces: Serializable, Measurable, Spatial, Bounded, Volume.

Title
-----
Interfaces Module

Context
-------
This module defines abstract interfaces used by geometry and models.
Serializable[T] requires serialize() -> T and unserialize(data) -> instance.
Measurable requires a size property (Decimal). Spatial requires contains
and intersects. Bounded requires a box property (Box). Volume requires
signed_area and supports __abs__. Geometry types and models implement
these for consistent persistence and spatial operations. Used for type
hints and to group behavior (e.g. Bounded.intersects via box).

Examples:
>>> isinstance(point, Spatial)
>>> box = segment.box  # Bounded
>>> data = model.serialize()  # Serializable
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any
from typing import Generic
from typing import TypeVar

if TYPE_CHECKING:
    from geometry.box import Box

T = TypeVar("T")


class Serializable(ABC, Generic[T]):
    """
    Abstract base for objects that support serialize() and unserialize() with type T.

    For example, to serialize and restore a model:
    >>> data = my_model.serialize()
    >>> obj = MyModel.unserialize(data)

    For example, to serialize and restore a polygon (list):
    >>> data = polygon.serialize()
    >>> obj = Polygon.unserialize(data)

    For example, to serialize and restore a point (str):
    >>> s = point.serialize()
    >>> obj = Point.unserialize(s)
    """

    @abstractmethod
    def serialize(self) -> T:
        """
        Return the serialized representation of this object (dict, list, str, etc.).

        For example, to export a model to a dict:
        >>> data = model.serialize()
        >>> isinstance(data, dict)
        True
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def unserialize(cls, data: Any) -> Serializable[T]:
        """
        Build an instance from serialized data. Subclasses must validate and coerce data.
        Always returns an instance of Serializable.

        For example, to build a model from a dict:
        >>> obj = MyModel.unserialize({"id": "abc", "created_at": "2024-01-01T00:00:00.000000Z"})
        >>> isinstance(obj, MyModel)
        True
        """
        raise NotImplementedError


class Bounded(ABC):
    """
    Abstract base for types that have an axis-aligned bounding box.

    For example, to get the bounding box of a segment:
    >>> box = segment.box
    >>> box.min_x, box.max_x
    (0, 10)
    """

    @property
    @abstractmethod
    def box(self) -> Box:
        """Return the axis-aligned bounding box."""
        ...


class Measurable(ABC):
    """
    Abstract base for types that have a numeric size (e.g. Interval length, Segment distance).

    For example, to get the length of an interval:
    >>> length = interval.size
    >>> isinstance(length, Decimal)
    True
    """

    @property
    @abstractmethod
    def size(self) -> Decimal:
        """Return the size (length, distance, etc.) as a Decimal."""
        ...


class Spatial(ABC):
    """
    Abstract base for types that support containment and intersection checks.

    For example, to check if a box contains a point:
    >>> box.contains(point)
    True
    For example, to check if two segments intersect:
    >>> seg1.intersects(seg2)
    False
    """

    @abstractmethod
    def contains(self, obj: Any, inclusive: bool = True) -> bool:
        """Return True if this object contains obj (optionally with inclusive bounds)."""
        ...

    @abstractmethod
    def intersects(self, obj: Any, inclusive: bool = True) -> bool:
        """Return True if this object intersects obj (optionally with inclusive bounds)."""
        ...


class Volume(ABC):
    """
    Abstract base for types that have a signed area (e.g. Walk, Polygon).

    For example, to get the signed area of a polygon:
    >>> area = polygon.signed_area
    >>> abs_area = abs(polygon)
    """

    @property
    @abstractmethod
    def signed_area(self) -> Decimal:
        """Return the signed area as a Decimal. Raises NotImplementedError if not implemented."""
        raise NotImplementedError

    def __abs__(self) -> Decimal:
        """Return the absolute value of signed_area."""
        return abs(self.signed_area)
