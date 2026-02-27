"""
Task request: job_id and user_email for all tasks.

Title
-----
TaskRequest

Context
-------
TaskRequest is the TypedDict for task input: job_id (Identifier) and
user_email (Email). Both are required. Parsed from the SQS message body
by StartTask and ReportTask in validate(). The worker receives the body
from WorkerRequest and passes it to task.handle(body). Used for typing
and for building the validated input passed to execute().

Examples:
    TaskRequest(job_id=Identifier("abc"), user_email=Email("u@e.com"))
"""

from __future__ import annotations

from typing import TypedDict

from attributes import Email
from attributes import Identifier


class TaskRequest(TypedDict):
    """Task request: job_id and user_email."""

    job_id: Identifier
    user_email: Email
