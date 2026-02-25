"""
Status enum for task output: SUCCESS or FAILED.
"""

from __future__ import annotations

from enum import Enum

from exceptions import ValidationError


class Status(str, Enum):
    """Task status: PENDING, SUCCESS, or FAILED."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

    @classmethod
    def parse(cls, value: str | None) -> Status:
        """Coerce string to Status; raises ValidationError (400) if invalid."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError("status is required and must be a non-empty string")
        raw: str = value.strip().lower() if isinstance(value, str) else str(value).strip().lower()
        try:
            return cls(raw)
        except ValueError:
            raise ValidationError(
                f"status must be one of [{cls.PENDING.value!r}, {cls.FAILED.value!r}, {cls.SUCCESS.value!r}], got {raw!r}"
            )
