"""
SQS worker Lambda entry point.
"""

from __future__ import annotations

import logging
from typing import Any

from exceptions import InvalidActionError
from exceptions import ValidationError
from messages import Queue
from attributes import Action
from workers.request import Request
from workers.urls import TASK_BY_ACTION

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: dict[str, Any], context: Any) -> dict[str, list[dict[str, Any]]]:
    """
    Process SQS messages: dispatch by action to RunTask or ReportTask, then commit each message.

    Each record must have action ("run" or "report"), job_id, and user_email. Invalid
    messages are logged and appended to results with an "error" key; the message is
    still committed. If task execution fails, the exception is logged and the message
    is not committed so SQS can retry.

    Returns a dict with key "results", a list of task result dicts (or error dicts).
    """
    logger.info(
        "Worker handler received event keys: %s",
        list(event.keys()) if isinstance(event, dict) else type(event),
    )
    results: list[dict[str, Any]] = []
    queue: Queue = Queue()
    for request in Request.from_records(event):
        try:
            action: Action = request.action
            body: dict[str, Any] = request.body
            logger.info(
                "Processing request action=%s job_id=%s",
                str(action),
                request.job_id,
            )
        except (ValidationError, InvalidActionError) as err:
            logger.warning("Invalid request: %s", err)
            results.append({"error": str(err)})
            continue

        task_class = TASK_BY_ACTION.get(action)
        if task_class is None:
            results.append({"error": f"Unknown action: {action}"})
        else:
            results.append(task_class().handle(body=body))

        try:
            queue.commit(request.message)
        except Exception as err:
            logger.exception("Failed to commit message: %s", err)

    return {"results": results}
