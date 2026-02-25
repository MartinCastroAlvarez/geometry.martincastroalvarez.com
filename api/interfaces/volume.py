"""
Volume abstract base: defines signed_area and __abs__ (absolute signed area).
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from decimal import Decimal


class Volume(ABC):
    """Abstract base for types that have a signed area (e.g. Path, Polygon)."""

    @property
    @abstractmethod
    def signed_area(self) -> Decimal:
        """Return the signed area as a Decimal. Raises NotImplementedError if not implemented."""
        raise NotImplementedError

    def __abs__(self) -> Decimal:
        """Return the absolute value of signed_area."""
        return abs(self.signed_area)
