"""
SQS queue operations for the geometry API.

Title
-----
Queue (SQS Client)

Context
-------
Queue wraps SQS for the geometry job queue. Queue name from QUEUE_NAME env;
missing raises ConfigurationError. put(message, delay_seconds) sends a
message (JSON body from message.serialize()). receive(max_messages, wait_time_seconds)
returns raw SQS message list (body, receiptHandle). delete(receipt_handle)
removes a message; commit(message) calls delete when message has receipt_handle.
Used by JobMutation (put after create), StartTask and ReportTask (put REPORT),
and worker handler (receive, process, commit). SQS errors raise ServiceUnavailableError.

Examples:
    queue = Queue()
    queue.put(Message(action=Action.START, job_id=job_id, user_email=user.email))
    for raw in queue.receive(max_messages=5):
        msg = Message.unserialize({**json.loads(raw["body"]), "receipt_handle": raw["receiptHandle"]})
        process(msg)
        queue.commit(msg)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import boto3
from attributes import ReceiptHandle
from botocore.exceptions import ClientError
from exceptions import ConfigurationError
from exceptions import ServiceUnavailableError
from exceptions import ValidationError

from api.logger import get_logger

from .message import Message

logger = get_logger(__name__)
QUEUE_NAME: str | None = os.getenv("QUEUE_NAME")


@dataclass
class Queue:
    """
    SQS queue operations. Queue name from QUEUE_NAME env.

    Example:
    >>> queue = Queue()
    >>> queue.put(Message(action=Action.START, job_id=job_id, user_email=user.email))
    >>> for raw in queue.receive(max_messages=5):
    ...     msg = Message.unserialize({**json.loads(raw["body"]), "receipt_handle": raw["receiptHandle"]})
    ...     process(msg)
    ...     queue.commit(msg)
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
        wait_time_seconds: int = 20,
    ) -> list[dict[str, Any]]:
        if max_messages < 1 or max_messages > 10:
            raise ValidationError("Max messages must be between 1 and 10")
        if wait_time_seconds < 0 or wait_time_seconds > 20:
            raise ValidationError("Wait time seconds must be between 0 and 20")
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
        handle = ReceiptHandle(receipt_handle) if not isinstance(receipt_handle, ReceiptHandle) else receipt_handle
        try:
            self.client.delete_message(QueueUrl=self.url, ReceiptHandle=handle)
        except ClientError as err:
            logger.error("Queue.delete() | delete_message failed error=%s", str(err))
            raise ServiceUnavailableError(f"SQS service error: {str(err)}") from err

    def commit(self, message: Message) -> None:
        if not message.receipt_handle:
            return
        self.delete(message.receipt_handle)
