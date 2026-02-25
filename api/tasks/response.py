"""
Task response: status plus optional job_id, error, traceback. Tasks add reason/job via subclasses.
"""

from __future__ import annotations

from typing import NotRequired
from typing import TypedDict

from attributes import Identifier
from enums import Status


class TaskResponse(TypedDict):
    """Task output: status (required); optional job_id, error, traceback."""

    status: Status
    job_id: NotRequired[Identifier]
    error: NotRequired[str]
    traceback: NotRequired[list[str]]
