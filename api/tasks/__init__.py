"""
Background tasks invoked by the worker Lambda.

Title
-----
Tasks Package

Context
-------
This package defines the worker tasks: StartTask and ReportTask. Task is
the base (validate, execute, handle). StartTask logs job stdin and
enqueues a REPORT message; returns FAILED if job already failed.
ReportTask loads job and children, merges children stdout/stderr into
job, sets status (SUCCESS/FAILED), saves, and notifies parent with
REPORT. TaskRequest has job_id and user_email; TaskResponse has status
and optional job_id, error, traceback. Used by workers.handler and
workers.urls (TASK_BY_ACTION).

Examples:
>>> task = StartTask()
>>> result = task.handle(body={"job_id": "abc", "user_email": "u@e.com"})
"""

from tasks.base import Task
from tasks.report import ReportTask
from tasks.request import TaskRequest
from tasks.response import ReportTaskResponse
from tasks.response import StartTaskResponse
from tasks.response import TaskResponse
from tasks.start import StartTask

__all__ = [
    "ReportTask",
    "ReportTaskResponse",
    "StartTask",
    "StartTaskResponse",
    "Task",
    "TaskRequest",
    "TaskResponse",
]
