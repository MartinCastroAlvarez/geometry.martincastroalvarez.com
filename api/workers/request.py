"""
Worker request parsed from a single SQS message body.
"""

from __future__ import annotations

import json
import logging
from typing import Any
from typing import Iterator

from exceptions import InvalidActionError
from exceptions import ValidationError
from messages import Message
from attributes import Action

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Request:
    """
    Worker request parsed from a single SQS message body.

    Validates and exposes action (as Action), job_id, user_email. Used to build the task body
    and to commit the message after processing.

    Example:
    >>> req = Request(message_data, receipt_handle)
    >>> req.action == Action.RUN
    True
    >>> queue.commit(req.message)
    """

    def __init__(
        self,
        data: dict[str, Any],
        receipt_handle: str | None = None,
    ) -> None:
        self.data = data
        self.receipt_handle = receipt_handle

    @property
    def action(self) -> Action:
        raw = self.data.get("action")
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            raise ValidationError("action is required and must be a string")
        return Action(str(raw).strip().lower())

    @property
    def job_id(self) -> str:
        raw = self.data.get("job_id")
        if not raw or not isinstance(raw, str):
            raise ValidationError("job_id is required and must be a non-empty string")
        return raw

    @property
    def user_email(self) -> str:
        raw = self.data.get("user_email")
        if not raw or not isinstance(raw, str):
            raise ValidationError("user_email is required and must be a non-empty string")
        return raw

    @property
    def message(self) -> Message:
        return Message.from_dict(
            {**self.data, "receipt_handle": self.receipt_handle}
        )

    @property
    def body(self) -> dict[str, Any]:
        return {"job_id": self.job_id, "user_email": self.user_email}

    @classmethod
    def from_records(cls, event: dict[str, Any]) -> Iterator[Request]:
        """
        Yield a Request for each SQS record in the event, or a single Request for EventBridge/empty payloads.
        """
        if "Records" in event:
            for record in event["Records"]:
                body = record.get("body", "{}")
                receipt_handle = record.get("receiptHandle")
                try:
                    message_data = json.loads(body) if body else {}
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in SQS message body: %s", body)
                    message_data = {}
                yield cls(message_data, receipt_handle)
        else:
            yield cls(event or {})
