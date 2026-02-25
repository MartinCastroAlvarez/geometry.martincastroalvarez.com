"""
Task request: base with job_id; subclasses add user_email for StartTask / ReportTask.
"""

from __future__ import annotations

from typing import TypedDict

from attributes import Email
from attributes import Identifier


class TaskRequest(TypedDict):
    """Base task request: job_id (Identifier)."""

    job_id: Identifier


class StartTaskRequest(TaskRequest):
    """Start task: job_id and user_email."""

    user_email: Email


class ReportTaskRequest(TaskRequest):
    """Report task: job_id and user_email."""

    user_email: Email
