"""
Title type: string with configurable min and max length validation.

Title
-----
Title Attribute

Context
-------
Title is a string subclass used for gallery titles, user display names,
and other short text that must be non-empty (by default) and bounded in
length. The constructor accepts any value; None or non-string raises
ValidationError. The string is stripped; if length is below min_length
or above max_length, ValidationError is raised. Default min_length=1,
max_length=200. Use min_length=0 for optional display names (e.g. User).

Examples:
    Title("My Gallery", min_length=1, max_length=100)
    Title("", min_length=1, max_length=100)  # ValidationError
    Title("", min_length=0, max_length=200)  # allowed for optional name
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
