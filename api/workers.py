"""
SQS worker Lambda: request parsing, routing (ROUTES), and handler.

Title
-----
Workers Module

Context
-------
This module implements the SQS worker Lambda entry point. handler(event, context)
processes SQS records (or a single EventBridge-style payload): parses
WorkerRequest, dispatches by action to StartTask or ReportTask via ROUTES,
commits each message after processing. WorkerRequest parses body and receipt_handle;
WorkerResponse holds results (list of TaskResponse). Invalid messages
are logged and appended with error; failed task execution does not commit
so SQS can retry.

Examples:
>>> from workers import handler, WorkerRequest, WorkerResponse
>>> result = handler(sqs_event, context)
"""

from __future__ import annotations

import json
from typing import Any
from typing import Iterator
from typing import Type

from attributes import Email
from attributes import Identifier
from attributes import ReceiptHandle
from enums import Action
from enums import Status
from interfaces import Serializable
from logger import get_logger
from messages import Message
from messages import Queue
from tasks import ReportTask
from tasks import StartTask
from tasks import Task
from tasks import TaskResponse

logger = get_logger(__name__)


ROUTES: dict[Action, Type[Task]] = {
    Action.START: StartTask,
    Action.REPORT: ReportTask,
}


class WorkerRequest(Serializable[dict[str, Any]]):
    """
    Worker request parsed from a single SQS message body.

    Validates and exposes action (as Action), job_id, user_email. Used to build the task body
    and to commit the message after processing.

    Example:
    >>> req = WorkerRequest(message_data, receipt_handle)
    >>> req.action == Action.START
    True
    >>> queue.commit(req.message)
    """

    def __init__(
        self,
        data: dict[str, Any],
        receipt_handle: ReceiptHandle,
    ) -> None:
        self.data = data
        self.receipt_handle = receipt_handle

    def serialize(self) -> dict[str, Any]:
        raise NotImplementedError("WorkerRequest.serialize is not used")

    @property
    def action(self) -> Action:
        return Action.parse(self.data.get("action"))

    @property
    def job_id(self) -> Identifier:
        return Identifier(self.data.get("job_id"))

    @property
    def user_email(self) -> Email:
        return Email(self.data.get("user_email"))

    @property
    def message(self) -> Message:
        return Message.unserialize({**self.data, "receipt_handle": str(self.receipt_handle)})

    @property
    def body(self) -> dict[str, Any]:
        out: dict[str, Any] = {"job_id": str(self.job_id), "user_email": str(self.user_email)}
        meta = self.data.get("meta")
        if isinstance(meta, dict):
            out["meta"] = meta
        return out

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> WorkerRequest:
        """Build one WorkerRequest from a single record (SQS record with body/receiptHandle or message dict)."""
        if "body" in data:
            body: str = data.get("body", "{}")
            try:
                message_data: dict[str, Any] = json.loads(body) if body else {}
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in SQS message body: %s", body)
                message_data = {}
            receipt_handle: ReceiptHandle = ReceiptHandle(data.get("receiptHandle"))
            return cls(message_data, receipt_handle)
        receipt_handle = ReceiptHandle(data.get("receipt_handle"))
        return cls(data or {}, receipt_handle)

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> Iterator[WorkerRequest]:
        """
        Yield a WorkerRequest for each SQS record in the event, or a single WorkerRequest for EventBridge/empty payloads.
        """
        if "Records" in event:
            for record in event["Records"]:
                yield cls.unserialize(record)
        else:
            yield cls.unserialize(event or {})


class WorkerResponse(Serializable[dict[str, Any]]):
    """Handler return value: results list of TaskResponse."""

    def __init__(self, results: list[TaskResponse]) -> None:
        self.results: list[TaskResponse] = results

    def serialize(self) -> dict[str, Any]:
        serialized: list[dict[str, Any]] = []
        for item in self.results:
            out: dict[str, Any] = {}
            for key, value in item.items():
                if value is None:
                    out[key] = None
                elif isinstance(value, Status):
                    out[key] = value.value
                elif isinstance(value, Identifier):
                    out[key] = str(value)
                else:
                    out[key] = value
            serialized.append(out)
        return {"results": serialized}

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> WorkerResponse:
        raise NotImplementedError("WorkerResponse.unserialize is not used")


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Process SQS messages: dispatch by action to StartTask or ReportTask, then commit each message.

    Each record must have action ("start" or "report"), job_id, and user_email. Invalid
    messages are logged and appended to results with an "error" key; the message is
    still committed. If task execution fails, the exception is logged and the message
    is not committed so SQS can retry. The worker always processes all messages.

    Returns a JSON-serializable dict with key "results" (list of task result dicts).
    """
    logger.info(
        "handler.handler() | received event keys=%s",
        list(event.keys()) if isinstance(event, dict) else type(event),
    )
    results: list[TaskResponse] = []
    queue: Queue = Queue()
    for request in WorkerRequest.from_event(event):
        try:
            action: Action = request.action
            body: dict[str, Any] = request.body
            logger.info(
                "handler.handler() | processing request action=%s job_id=%s",
                action.value,
                request.job_id,
            )
            out: TaskResponse = ROUTES[action]().handler(body=body)
        except Exception as err:
            logger.exception("handler.handler() | processing request failed error=%s", err)
            out = {"status": Status.FAILED, "error": str(err)}
        finally:
            logger.info(
                "handler.handler() | processing request completed action=%s job_id=%s",
                action.value,
                request.job_id,
            )
            results.append(out)
            queue.commit(request.message)

    response = WorkerResponse(results=results)
    payload = response.serialize()
    return json.loads(json.dumps(payload, default=str))
