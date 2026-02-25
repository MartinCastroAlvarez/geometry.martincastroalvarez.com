"""
Signature type: deterministic hash (SHA-256 truncated to LENGTH bytes) for use in __hash__.
"""

from __future__ import annotations

import hashlib
from typing import Any

from exceptions import ValidationError


class Signature(int):
    """
    An integer derived from hashing a value (for use as __hash__).
    Constructor accepts Any; if not None, the value is cast to str in a deterministic way
    (str(value)) before hashing, so callers need not cast. None raises; empty string becomes ":empty:".

    Example:
    >>> s = Signature("point:1:2")
    >>> s = Signature([1, 2])  # str([1, 2]) used
    """

    LENGTH: int = 32

    def __new__(cls, value: Any) -> Signature:
        if value is None:
            raise ValidationError("Signature value must not be None")
        if not isinstance(value, str):
            value = str(value)
        if len(value) == 0:
            value = ":empty:"
        raw: bytes = value.encode()
        hashed: bytes = hashlib.sha256(raw).digest()[: cls.LENGTH]
        int_value: int = int.from_bytes(hashed, "big")
        return super().__new__(cls, int_value)

    def __hash__(self) -> Signature:
        return self
