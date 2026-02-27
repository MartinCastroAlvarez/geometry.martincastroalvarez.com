"""
Measurable abstract base: defines the abstract size property.

Title
-----
Measurable Interface

Context
-------
Measurable is the abstract base for types that have a numeric size:
length, distance, area, etc. The only requirement is a property size
returning Decimal. Interval and Segment implement it (interval length,
segment Euclidean length). Used for type hints and where code needs to
compare or aggregate sizes across different geometry types.

Examples:
    segment.size  # Euclidean length
    interval.size  # end - start
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
