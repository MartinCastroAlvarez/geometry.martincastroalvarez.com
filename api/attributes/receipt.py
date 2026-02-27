"""
ReceiptHandle type: non-empty string (e.g. SQS receipt handle).

Title
-----
ReceiptHandle Attribute

Context
-------
ReceiptHandle is a non-empty string used for SQS message receipt handles.
After processing a message, the worker calls queue.delete(receipt_handle)
(or queue.commit(message)) so SQS removes the message. None, non-string,
or empty raise ValidationError. The Message dataclass can hold an optional
receipt_handle so the worker can commit after handling. Used in messages.Message
and workers.request.WorkerRequest.

Examples:
>>> handle = ReceiptHandle("abc123-receipt-handle")
>>> message = Message.unserialize({..., "receipt_handle": str(handle)})
>>> queue.commit(message)
"""

from __future__ import annotations

from typing import Any

from exceptions import ValidationError


class ReceiptHandle(str):
    """
    A non-empty string, e.g. SQS message receipt handle.
    Raises ValidationError for None, non-string, or empty value.

    Example:
    >>> handle = ReceiptHandle("abc123-receipt-handle")
    """

    def __new__(cls, value: Any = None) -> ReceiptHandle:
        if value is None:
            raise ValidationError("Receipt handle is required")
        if not isinstance(value, str):
            raise ValidationError("Receipt handle must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Receipt handle must be a non-empty string")
        return super().__new__(cls, raw)
