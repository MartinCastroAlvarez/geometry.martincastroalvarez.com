"""
Worker request parsed from a single SQS message body.

Title
-----
WorkerRequest

Context
-------
WorkerRequest wraps one SQS message: data (parsed body dict) and
receipt_handle. Properties action, job_id, user_email, message, body
expose typed values for the handler and tasks. unserialize(record) builds
from SQS record (body string + receiptHandle) or from a plain dict with
receipt_handle. from_event(event) yields one WorkerRequest per Records[]
entry, or one from the event itself for non-SQS invocations. Used by
workers.handler to parse and to commit (message.receipt_handle).

Examples:
    for request in WorkerRequest.from_event(event):
        task_class = TASK_BY_ACTION[request.action]
        task_class().handle(body=request.body)
        queue.commit(request.message)
"""

from __future__ import annotations

import json
import logging
from typing import Any
from typing import Iterator

from attributes import Email
from attributes import Identifier
from attributes import ReceiptHandle
from enums import Action
from interfaces import Serializable
from messages import Message

logger = logging.getLogger()
logger.setLevel(logging.INFO)


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
        return {"job_id": str(self.job_id), "user_email": str(self.user_email)}

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
