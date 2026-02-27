"""
Spatial abstract base: defines contains and intersects.

Title
-----
Spatial Interface

Context
-------
Spatial is the abstract base for types that support containment and
intersection tests. contains(obj, inclusive) returns True if this
object contains obj (Point, Segment, etc.). intersects(obj, inclusive)
returns True if this object intersects obj. The inclusive flag controls
boundary behavior. Box, Segment, Polygon, and Interval implement
Spatial. Used for point-in-polygon, segment intersection, and
visibility/guard logic.

Examples:
>>> box.contains(point)
>>> segment.intersects(other_segment)
>>> polygon.contains(point)
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class Spatial(ABC):
    """Abstract base for types that support containment and intersection checks."""

    @abstractmethod
    def contains(self, obj: Any, inclusive: bool = True) -> bool:
        """Return True if this object contains obj (optionally with inclusive bounds)."""
        ...

    @abstractmethod
    def intersects(self, obj: Any, inclusive: bool = True) -> bool:
        """Return True if this object intersects obj (optionally with inclusive bounds)."""
        ...
