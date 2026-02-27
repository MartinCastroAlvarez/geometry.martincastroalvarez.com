"""
Bounded abstract base: defines the box property (axis-aligned bounding box).

Title
-----
Bounded Interface

Context
-------
Bounded is the abstract base for types that have an axis-aligned bounding
box. The box property returns a Box. Segment and Polygon implement it;
Box.intersects(Bounded) delegates to box.intersects(obj.box). Used for
fast broad-phase tests before detailed geometry (e.g. segment-segment
intersection checks box first). TYPE_CHECKING import avoids circular
dependency with geometry.box.

Examples:
    box = segment.box
    if box1.intersects(polygon.box): ...
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geometry.box import Box


class Bounded(ABC):
    """Abstract base for types that have an axis-aligned bounding box."""

    @property
    @abstractmethod
    def box(self) -> Box:
        """Return the axis-aligned bounding box."""
        ...
