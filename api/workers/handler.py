"""
SQS worker Lambda entry point.
"""

from __future__ import annotations

import logging
import traceback
from typing import Any

from enums import Action
from enums import Status
from exceptions import InvalidActionError
from exceptions import ValidationError
from messages import Queue
from tasks.response import TaskResponse
from workers.request import WorkerRequest
from workers.response import WorkerResponse
from workers.urls import TASK_BY_ACTION

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event: dict[str, Any], context: Any) -> WorkerResponse:
    """
    Process SQS messages: dispatch by action to StartTask or ReportTask, then commit each message.

    Each record must have action ("start" or "report"), job_id, and user_email. Invalid
    messages are logged and appended to results with an "error" key; the message is
    still committed. If task execution fails, the exception is logged and the message
    is not committed so SQS can retry. The worker always processes all messages.

    Returns a WorkerResponse with results as list of TaskResponse.
    """
    logger.info(
        "Worker handler received event keys: %s",
        list(event.keys()) if isinstance(event, dict) else type(event),
    )
    results: list[TaskResponse] = []
    queue: Queue = Queue()
    for request in WorkerRequest.from_event(event):
        try:
            action: Action = request.action
            body: dict[str, Any] = request.body
            logger.info(
                "Processing request action=%s job_id=%s",
                action.value,
                request.job_id,
            )
        except (ValidationError, InvalidActionError) as err:
            logger.warning("Invalid request: %s", err)
            results.append({"status": Status.FAILED, "error": str(err)})
            continue

        task_class = TASK_BY_ACTION.get(action)
        if task_class is None:
            results.append({"status": Status.FAILED, "error": f"Unknown action: {action.value}"})
        else:
            try:
                out: TaskResponse = task_class().handle(body=body)
                results.append(out)
            except Exception as err:
                logger.exception("Task failed: %s", err)
                results.append(
                    {
                        "status": Status.FAILED,
                        "error": f"{type(err).__name__}: {err}",
                        "traceback": traceback.format_exception(type(err), err, err.__traceback__),
                    }
                )

        try:
            queue.commit(request.message)
        except Exception as err:
            logger.exception("Failed to commit message: %s", err)

    return WorkerResponse(results=results)
