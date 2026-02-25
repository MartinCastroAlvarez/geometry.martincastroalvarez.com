"""
SQS message format for the geometry API.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from exceptions import ValidationError
from interfaces import Serializable
from attributes import Action
from attributes import Email


@dataclass
class Message(Serializable):
    """
    Message for geometry queue. action is Action (RUN or REPORT); job_id and user_email required.

    Example:
    >>> msg = Message(action=Action("run"), job_id="abc123", user_email=Email("user@example.com"))
    >>> queue.put(msg)
    >>> msg = Message.from_dict({"action": "run", "job_id": "x", "user_email": "y", "receipt_handle": "rh"})
    >>> queue.commit(msg)
    """

    action: Action
    job_id: str
    user_email: Email
    metadata: dict[str, Any] = field(default_factory=dict)
    receipt_handle: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.action, Action):
            self.action = Action(str(self.action))
        if not self.job_id or not isinstance(self.job_id, str):
            raise ValidationError("job_id is required and must be a non-empty string")
        if not isinstance(self.user_email, Email):
            self.user_email = Email(str(self.user_email))

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "action": str(self.action),
            "job_id": self.job_id,
            "user_email": str(self.user_email),
        }
        if self.metadata:
            data["metadata"] = self.metadata
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Message:
        if not isinstance(data, dict):
            raise ValidationError("Message data must be a dictionary")
        action_val = data.get("action")
        if action_val is None:
            raise ValidationError("action is required")
        action = Action(str(action_val).strip().lower())
        job_id = str(data.get("job_id", ""))
        if not job_id:
            raise ValidationError("job_id is required and must be a non-empty string")
        user_email = Email(str(data.get("user_email", "")).strip())
        return cls(
            action=action,
            job_id=job_id,
            user_email=user_email,
            metadata=dict(data.get("metadata") or {}),
            receipt_handle=data.get("receipt_handle"),
        )
