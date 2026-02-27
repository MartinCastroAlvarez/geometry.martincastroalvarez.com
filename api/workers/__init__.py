"""
SQS worker Lambda: request parsing and handler.

Title
-----
Workers Package

Context
-------
This package implements the SQS worker Lambda entry point. handler(event, context)
processes SQS records (or a single EventBridge-style payload): parses
WorkerRequest, dispatches by action to StartTask or ReportTask, commits
each message after processing. WorkerRequest parses body and receipt_handle;
WorkerResponse holds results (list of TaskResponse). Invalid messages
are logged and appended with error; failed task execution does not commit
so SQS can retry. TASK_BY_ACTION in workers.urls maps Action to Task class.

Examples:
    from workers import handler, WorkerRequest, WorkerResponse
    result = handler(sqs_event, context)
"""

from workers.handler import handler
from workers.request import WorkerRequest
from workers.response import WorkerResponse

__all__ = ["handler", "WorkerRequest", "WorkerResponse"]
