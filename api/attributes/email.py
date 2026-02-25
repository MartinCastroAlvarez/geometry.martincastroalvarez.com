"""
Email type: string validated as a valid email format.
"""

from __future__ import annotations

import re
from typing import Any

from exceptions import ValidationError

from attributes.signature import Signature
from attributes.slug import Slug


class Email(str):
    """
    A string that must be a valid email format. Raises ValidationError (400) if invalid.

    Example:
    >>> e = Email("user@example.com")
    >>> Email("invalid")  # raises ValidationError
    """

    # Simple pattern: local@domain.tld (covers most common addresses)
    PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __new__(cls, value: Any = None) -> Email:
        if value is None:
            raise ValidationError("Email is required")
        if not isinstance(value, str):
            raise ValidationError("Email must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Email must be a non-empty string")
        if not cls.PATTERN.match(raw):
            raise ValidationError("Email must be a valid email address")
        return super().__new__(cls, raw)

    @property
    def slug(self) -> Slug:
        """
        URL-safe identifier for this email: Slug(email) + '-' + Signature(email).
        Using the signature avoids collisions when two emails slugify to the same string.
        """
        return Slug(f"{Slug(self)}-{Signature(self)}")
