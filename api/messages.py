"""
SQS message format and queue operations for the geometry API.

Title
-----
Messages Module (SQS)

Context
-------
This module defines the SQS message format and queue client for the
geometry API. Message carries action (START/REPORT), job_id, user_email,
and optional receipt_handle. Queue uses QUEUE_NAME env, provides put(),
receive(), delete(), and commit(message). Workers receive messages,
parse with Message.unserialize, run the task, and commit to remove from queue.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import boto3
from attributes import Email
from attributes import Identifier
from attributes import ReceiptHandle
from botocore.exceptions import ClientError
from enums import Action
from exceptions import ConfigurationError
from exceptions import ServiceUnavailableError
from exceptions import ValidationError
from interfaces import Serializable
from logger import get_logger
from settings import QUEUE_MAX_RECEIVE_MESSAGES
from settings import QUEUE_NAME
from settings import QUEUE_WAIT_TIME_SECONDS
from settings import QUEUE_WAIT_TIME_SECONDS_MAX

logger = get_logger(__name__)


@dataclass
class Message(Serializable[dict[str, Any]]):
    """
    Message for geometry queue. action is Action (START, REPORT); job_id and user_email required.

    For example, to create and serialize a start message:
    >>> msg = Message(action=Action.START, job_id=Identifier("j1"), user_email=Email("u@e.com"))
    >>> msg.serialize()
    {'action': 'start', 'job_id': 'j1', 'user_email': 'u@e.com'}
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
        """
        Build Message from dict (e.g. SQS body). Parses action, job_id, user_email.

        For example, to parse a received SQS message body:
        >>> msg = Message.unserialize({"action": "start", "job_id": "j1", "user_email": "u@e.com"})
        >>> msg.action
        <Action.START: 'start'>
        """
        if not isinstance(data, dict):
            raise ValidationError("Message data must be a dictionary")
        return cls(
            action=Action.parse(data.get("action")),
            job_id=Identifier(data.get("job_id")),
            user_email=Email(str(data.get("user_email", "")).strip()),
            receipt_handle=(ReceiptHandle(r) if (r := data.get("receipt_handle")) else None),
        )


@dataclass
class Queue:
    """
    SQS queue operations. Queue name from QUEUE_NAME env.

    For example, to enqueue a start message:
    >>> queue = Queue()
    >>> msg = Message(action=Action.START, job_id=Identifier("j1"), user_email=Email("u@e.com"))
    >>> message_id = queue.put(msg)
    """

    _client: Any = field(default=None, init=False, repr=False)

    @property
    def name(self) -> str:
        if not QUEUE_NAME:
            raise ConfigurationError("QUEUE_NAME environment variable is required")
        return QUEUE_NAME

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = boto3.client("sqs")
        return self._client

    @property
    def url(self) -> str:
        try:
            response = self.client.get_queue_url(QueueName=self.name)
            return response["QueueUrl"]
        except ClientError as err:
            logger.error("Queue.url | get_queue_url failed queue=%s error=%s", self.name, str(err))
            raise ServiceUnavailableError(f"SQS service error: {str(err)}") from err

    def put(self, message: Message, delay_seconds: int = 0) -> str:
        """
        Send a message to the queue. Returns SQS MessageId.

        For example, to enqueue a report message:
        >>> queue.put(Message(action=Action.REPORT, job_id=job.id, user_email=email))
        'abc-123-message-id'
        """
        if not isinstance(message, Message):
            raise ValidationError("Message must be a Message instance")
        if delay_seconds < 0 or delay_seconds > 900:
            raise ValidationError("Delay seconds must be between 0 and 900")
        try:
            json_message = json.dumps(message.serialize())
            params: dict[str, Any] = {"QueueUrl": self.url, "MessageBody": json_message}
            if delay_seconds > 0:
                params["DelaySeconds"] = delay_seconds
            response = self.client.send_message(**params)
            message_id = response["MessageId"]
            logger.debug("Queue.put() | action=%s job_id=%s message_id=%s", message.action.value, message.job_id, message_id)
            return message_id
        except (TypeError, ValueError) as err:
            raise ValidationError(f"Message is not JSON serializable: {str(err)}") from err
        except ClientError as err:
            logger.error("Queue.put() | send_message failed action=%s job_id=%s error=%s", message.action.value, message.job_id, str(err))
            raise ServiceUnavailableError(f"SQS service error: {str(err)}") from err

    def receive(
        self,
        max_messages: int = 1,
        wait_time_seconds: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Receive messages from the queue. Returns list of SQS message dicts (Body, ReceiptHandle, etc.).

        For example, to receive and process one message:
        >>> raw = queue.receive(max_messages=1)
        >>> if raw:
        ...     msg = Message.unserialize(json.loads(raw[0]["Body"]))
        """
        if wait_time_seconds is None:
            wait_time_seconds = QUEUE_WAIT_TIME_SECONDS
        if max_messages < 1 or max_messages > QUEUE_MAX_RECEIVE_MESSAGES:
            raise ValidationError(f"Max messages must be between 1 and {QUEUE_MAX_RECEIVE_MESSAGES}")
        if wait_time_seconds < 0 or wait_time_seconds > QUEUE_WAIT_TIME_SECONDS_MAX:
            raise ValidationError(f"Wait time seconds must be between 0 and {QUEUE_WAIT_TIME_SECONDS_MAX}")
        try:
            response = self.client.receive_message(
                QueueUrl=self.url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time_seconds,
                AttributeNames=["All"],
                MessageAttributeNames=["All"],
            )
            return response.get("Messages", [])
        except ClientError as err:
            logger.error("Queue.receive() | receive_message failed error=%s", str(err))
            raise ServiceUnavailableError(f"SQS service error: {str(err)}") from err

    def delete(self, receipt_handle: ReceiptHandle | str) -> None:
        """
        Delete a message by receipt handle (after processing).

        For example, to remove a processed message:
        >>> queue.delete(message["ReceiptHandle"])
        """
        handle = ReceiptHandle(receipt_handle) if not isinstance(receipt_handle, ReceiptHandle) else receipt_handle
        try:
            self.client.delete_message(QueueUrl=self.url, ReceiptHandle=handle)
        except ClientError as err:
            logger.error("Queue.delete() | delete_message failed error=%s", str(err))
            raise ServiceUnavailableError(f"SQS service error: {str(err)}") from err

    def commit(self, message: Message) -> None:
        """
        Delete the message from the queue (ack after processing). No-op if no receipt_handle.

        For example, to acknowledge after handling:
        >>> msg.receipt_handle = ReceiptHandle(raw["ReceiptHandle"])
        >>> queue.commit(msg)
        """
        if not message.receipt_handle:
            return
        self.delete(message.receipt_handle)
