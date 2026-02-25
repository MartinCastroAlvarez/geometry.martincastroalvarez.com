"""
Measurable abstract base: defines the abstract size property.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from decimal import Decimal


class Measurable(ABC):
    """Abstract base for types that have a numeric size (e.g. Interval length, Segment distance)."""

    @property
    @abstractmethod
    def size(self) -> Decimal:
        """Return the size (length, distance, etc.) as a Decimal."""
        ...
