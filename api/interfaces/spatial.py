"""
Spatial abstract base: defines contains and intersects.
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
