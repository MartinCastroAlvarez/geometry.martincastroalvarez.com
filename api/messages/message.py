"""
SQS message format for the geometry API.

Title
-----
Message (SQS Payload)

Context
-------
Message is the dataclass for a single SQS message: action (Action),
job_id (Identifier), user_email (Email), and optional receipt_handle
(ReceiptHandle). __post_init__ coerces action, job_id, user_email,
receipt_handle from raw values. serialize() produces the dict sent as
message body; unserialize() builds from body dict (e.g. from receive_message)
plus receipt_handle for commit. Used by Queue.put, WorkerRequest.message,
and queue.commit(message).

Examples:
    msg = Message(action=Action.START, job_id="abc123", user_email=Email("u@e.com"))
    queue.put(msg)
    msg = Message.unserialize({"action": "start", "job_id": "x", "user_email": "y", "receipt_handle": "rh"})
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from attributes import Email
from attributes import Identifier
from attributes import ReceiptHandle
from enums import Action
from exceptions import ValidationError
from interfaces import Serializable


@dataclass
class Message(Serializable[dict[str, Any]]):
    """
    Message for geometry queue. action is Action (START, REPORT); job_id and user_email required.

    Example:
    >>> msg = Message(action=Action.START, job_id="abc123", user_email=Email("user@example.com"))
    >>> queue.put(msg)
    >>> msg = Message.unserialize({"action": "start", "job_id": "x", "user_email": "y", "receipt_handle": "rh"})
    >>> queue.commit(msg)
    """

    action: Action
    job_id: Identifier
    user_email: Email
    receipt_handle: ReceiptHandle | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.action, Action):
            self.action = Action.parse(str(self.action))
        if not isinstance(self.job_id, Identifier):
            self.job_id = Identifier(self.job_id)
        if not isinstance(self.user_email, Email):
            self.user_email = Email(str(self.user_email))
        if self.receipt_handle is not None and not isinstance(self.receipt_handle, ReceiptHandle):
            self.receipt_handle = ReceiptHandle(self.receipt_handle)

    def serialize(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "job_id": str(self.job_id),
            "user_email": str(self.user_email),
        }

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> Message:
        if not isinstance(data, dict):
            raise ValidationError("Message data must be a dictionary")
        return cls(
            action=Action.parse(data.get("action")),
            job_id=Identifier(data.get("job_id")),
            user_email=Email(str(data.get("user_email", "")).strip()),
            receipt_handle=(ReceiptHandle(r) if (r := data.get("receipt_handle")) else None),
        )
