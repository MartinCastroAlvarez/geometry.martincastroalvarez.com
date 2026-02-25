"""
Task response: base and all task response subclasses.
"""

from __future__ import annotations

from typing import Any
from typing import NotRequired
from typing import TypedDict

from attributes import Identifier
from enums import Status


class TaskResponse(TypedDict):
    """Base task response: status (required); optional job_id, error, traceback."""

    status: Status
    job_id: NotRequired[Identifier]
    error: NotRequired[str]
    traceback: NotRequired[list[str]]


class StartTaskResponse(TaskResponse, total=False):
    """Start task response: status, job_id; optional reason when job failed."""

    reason: str


class ReportTaskResponse(TaskResponse, total=False):
    """Report task response: status, job_id; optional reason when failed; optional job when found."""

    reason: str
    job: dict[str, Any]
