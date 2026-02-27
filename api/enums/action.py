"""
Action enum for SQS worker messages: START or REPORT.

Title
-----
Worker Action Enum

Context
-------
Action indicates what the worker should do for a message: START (run the
job flow, enqueue report) or REPORT (aggregate children, update job status,
notify parent). parse(value) coerces a string; None or empty defaults to
START; invalid value raises InvalidActionError. Used in messages.Message
and workers.handler to select StartTask or ReportTask. The worker dispatches
by action via TASK_BY_ACTION.

Examples:
    action = Action.parse(body.get("action"))
    task_class = TASK_BY_ACTION[action]
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
            raise InvalidActionError(f"action must be one of [{cls.START.value!r}, {cls.REPORT.value!r}], got {raw!r}")
