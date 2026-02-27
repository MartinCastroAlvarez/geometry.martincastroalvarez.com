"""
Task response: base and all task response subclasses.

Title
-----
Task Response Types

Context
-------
TaskResponse is the base: status (Status), optional job_id, error,
traceback. StartTaskResponse adds reason (e.g. "job_failed").
ReportTaskResponse adds reason and job (serialized Job dict). Tasks
return these shapes; the worker collects them in WorkerResponse.results
and serializes for the Lambda return value. Used by workers.handler and
WorkerResponse.serialize().

Examples:
    return {"status": Status.SUCCESS, "job_id": job_id}
    return {"status": Status.FAILED, "error": str(e), "traceback": [...]}
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


class StartTaskResponse(TaskResponse):
    """Start task response: status, job_id; optional reason when job failed."""

    reason: str


class ReportTaskResponse(TaskResponse):
    """Report task response: status, job_id; optional reason when failed; optional job when found."""

    reason: str
    job: dict[str, Any]
