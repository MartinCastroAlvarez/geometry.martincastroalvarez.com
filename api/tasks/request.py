"""
Task request: job_id and user_email (validated input for StartTask / ReportTask).
"""

from __future__ import annotations

from typing import TypedDict

from attributes import Email
from attributes import Identifier


class TaskRequest(TypedDict):
    """Task input: job_id (Identifier) and user_email (Email)."""

    job_id: Identifier
    user_email: Email
