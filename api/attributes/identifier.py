"""
Identifier type: non-empty string with only alphanumeric, underscore, and dash.
"""

from __future__ import annotations

import re
from typing import Any

from exceptions import ValidationError


class Identifier(str):
    """
    A string identifier that allows only letters, digits, underscore (_), and dash (-).
    Raises ValidationError for empty or invalid characters.

    Example:
    >>> uid = Identifier("gallery_abc-123")
    >>> uid = Identifier("job_xyz")
    """

    # Only letters, digits, underscore, and hyphen
    PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

    def __new__(cls, value: Any = None) -> Identifier:
        if value is None:
            raise ValidationError("Identifier is required")
        if not isinstance(value, str):
            raise ValidationError("Identifier argument must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Identifier must be a non-empty string")
        if not cls.PATTERN.match(raw):
            raise ValidationError(
                "Identifier may only contain letters, digits, underscore (_), and dash (-)"
            )
        return super().__new__(cls, raw)
