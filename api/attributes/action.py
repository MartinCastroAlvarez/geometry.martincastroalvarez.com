"""
Action type for SQS worker messages: "run" or "report".
"""

from __future__ import annotations

from typing import Literal

from exceptions import InvalidActionError
from exceptions import ValidationError

ActionLiteral = Literal["run", "report"]


class Action(str):
    """
    Worker action: RUN ("run") or REPORT ("report"). Inherits from str.

    Use Action.RUN and Action.REPORT for comparisons. Invalid values raise ValidationError
    or InvalidActionError.

    Example:
    >>> a = Action("run")
    >>> a == Action.RUN
    True
    >>> a == Action.REPORT
    False
    """

    RUN: str = "run"
    REPORT: str = "report"

    def __new__(cls, value: str | None = None) -> Action:
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError("action is required and must be a non-empty string")
        raw: str = value.strip().lower() if isinstance(value, str) else str(value).strip().lower()
        if raw not in (cls.RUN, cls.REPORT):
            raise InvalidActionError(
                f"action must be one of [{cls.REPORT!r}, {cls.RUN!r}], got {raw!r}"
            )
        return super().__new__(cls, raw)
