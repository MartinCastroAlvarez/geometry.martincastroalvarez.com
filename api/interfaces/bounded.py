"""
Bounded abstract base: defines the box property (axis-aligned bounding box).
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
