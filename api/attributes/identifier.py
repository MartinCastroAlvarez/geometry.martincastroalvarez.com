"""
Identifier type: non-empty string with only alphanumeric, underscore, and dash.

Title
-----
Identifier Attribute

Context
-------
Identifier is a string subclass used for ids (job id, gallery id, index_id,
real_id). It allows only letters, digits, underscore (_), and hyphen (-).
None, non-string, non-int, empty string, or invalid characters raise
ValidationError. int is accepted and converted to str. Often used with
Signature to build deterministic ids (e.g. job id from boundary+obstacles,
gallery id from job_id and user email). Used in models, repositories,
indexes, and mutation/query request types.

Examples:
    Identifier("gallery_abc-123")
    Identifier(12345)
    Identifier(Signature(Email("user@example.com")))
"""

from __future__ import annotations

import re
from typing import Any

from exceptions import ValidationError


class Identifier(str):
    """
    A string identifier that allows only letters, digits, underscore (_), and dash (-).
    Accepts str or int (int is cast to str). Raises ValidationError for empty or invalid characters.

    Example:
    >>> uid = Identifier("gallery_abc-123")
    >>> uid = Identifier(Signature(Email("user@example.com")))
    """

    # Only letters, digits, underscore, and hyphen
    PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

    def __new__(cls, value: Any = None) -> Identifier:
        if value is None:
            raise ValidationError("Identifier is required")
        if isinstance(value, int):
            raw = str(value).strip()
        elif isinstance(value, str):
            raw = value.strip()
        else:
            raise ValidationError("Identifier argument must be a string or int")
        if not raw:
            raise ValidationError("Identifier must be a non-empty string")
        if not cls.PATTERN.match(raw):
            raise ValidationError("Identifier may only contain letters, digits, underscore (_), and dash (-)")
        return super().__new__(cls, raw)
