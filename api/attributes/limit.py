"""
Limit type for pagination: integer in [MIN, MAX], validated once.
"""

from __future__ import annotations

from typing import Any

from exceptions import ValidationError


class Limit(int):
    """
    A positive integer limit for pagination, at least MIN and at most MAX.
    Inherits from int; use in search/query limit and bucket limit.

    Example:
    >>> limit = Limit(20)
    >>> limit = Limit(100)
    >>> limit <= Limit.MAX
    True
    """

    MIN: int = 1
    # Reasonable upper bound for S3 list_objects_v2 and API pagination
    MAX: int = 1000

    def __new__(cls, value: Any = None) -> Limit:
        if value is None:
            value = 20
        try:
            raw: int = int(value)
        except (TypeError, ValueError):
            raise ValidationError("Limit must be an integer")
        if raw < cls.MIN:
            raise ValidationError(f"Limit must be at least {cls.MIN}")
        if raw > cls.MAX:
            raise ValidationError(f"Limit must be at most {cls.MAX}")
        return super().__new__(cls, raw)
