"""
Title type: string with configurable min and max length validation.
"""

from __future__ import annotations

from typing import Any

from exceptions import ValidationError


class Title(str):
    """
    A string title with length validation.

    Example:
    >>> Title("My Gallery", min_length=1, max_length=100)
    'My Gallery'
    >>> Title("", min_length=1, max_length=100)
    ValidationError: Title must be at least 1 character
    """

    def __new__(
        cls,
        value: Any,
        *,
        min_length: int = 1,
        max_length: int = 200,
    ) -> Title:
        if value is None:
            raise ValidationError("Title is required")
        if not isinstance(value, str):
            raise ValidationError("Title must be a string")
        raw: str = value.strip()
        if min_length > 0 and len(raw) < min_length:
            raise ValidationError(f"Title must be at least {min_length} character(s)")
        if len(raw) > max_length:
            raise ValidationError(f"Title must be at most {max_length} character(s)")
        return super().__new__(cls, raw)
