"""
ReceiptHandle type: non-empty string (e.g. SQS receipt handle).
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
