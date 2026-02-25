"""
Action enum for SQS worker messages: START or REPORT.
"""

from __future__ import annotations

from enum import Enum

from exceptions import InvalidActionError


class Action(str, Enum):
    """Worker action: START (default), REPORT."""

    START = "start"
    REPORT = "report"

    @classmethod
    def parse(cls, value: str | None) -> Action:
        """Coerce string to Action; default START if missing/empty; raises InvalidActionError (400) if invalid."""
        if value is None or (isinstance(value, str) and not value.strip()):
            return cls.START
        raw: str = value.strip().lower() if isinstance(value, str) else str(value).strip().lower()
        try:
            return cls(raw)
        except ValueError:
            raise InvalidActionError(
                f"action must be one of [{cls.START.value!r}, {cls.REPORT.value!r}], got {raw!r}"
            )
