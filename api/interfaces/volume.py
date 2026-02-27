"""
Volume abstract base: defines signed_area and __abs__ (absolute signed area).

Title
-----
Volume Interface

Context
-------
Volume is the abstract base for types that have a signed area: Polygon,
Walk. signed_area is positive for counter-clockwise, negative for
clockwise, zero for degenerate. __abs__ returns abs(signed_area). Used
for polygon orientation (is_ccw, is_cw), convexity, and area-based
comparisons. Walk uses it for turn direction; Polygon for winding and
convexity checks.

Examples:
>>> area = polygon.signed_area
>>> abs(polygon)  # absolute area
>>> walk.signed_area  # 2x2 determinant
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from decimal import Decimal


class Volume(ABC):
    """Abstract base for types that have a signed area (e.g. Walk, Polygon)."""

    @property
    @abstractmethod
    def signed_area(self) -> Decimal:
        """Return the signed area as a Decimal. Raises NotImplementedError if not implemented."""
        raise NotImplementedError

    def __abs__(self) -> Decimal:
        """Return the absolute value of signed_area."""
        return abs(self.signed_area)
