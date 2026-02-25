"""
Task request: job_id and user_email for all tasks.
"""

from __future__ import annotations

from typing import TypedDict

from attributes import Email
from attributes import Identifier


class TaskRequest(TypedDict):
    """Task request: job_id and user_email."""

    job_id: Identifier
    user_email: Email
