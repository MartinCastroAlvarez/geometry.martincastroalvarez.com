"""
Offset type: non-empty string for pagination next_token. Does not accept None.
"""

from __future__ import annotations

from typing import Any

from exceptions import ValidationError


class Offset(str):
    """
    A non-empty string for pagination (e.g. next_token).
    Does not accept None; use Offset | None where the token is optional.
    Raises ValidationError for None, non-string, or empty value.

    Example:
    >>> token = Offset("abc123")
    >>> token = Offset(body["next_token"])  # raises if missing or empty
    """

    def __new__(cls, value: Any) -> Offset:
        if value is None:
            raise ValidationError("Offset is required")
        if not isinstance(value, str):
            raise ValidationError("Offset must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Offset must be a non-empty string")
        return super().__new__(cls, raw)
