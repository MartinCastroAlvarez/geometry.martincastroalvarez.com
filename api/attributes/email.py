"""
Email type: string validated as a valid email format.

Title
-----
Email Attribute

Context
-------
Email is a string subclass validated with a regex for typical email format
(local@domain.tld). None, non-string, empty, or invalid format raise
ValidationError. The slug property returns a URL-safe identifier for the
email (Slug(email) + '-' + Signature(email)) to avoid collisions when
different emails slugify to the same string. Used for user identity, owner_email,
and in JWT payloads and task messages.

Examples:
>>> Email("user@example.com")
>>> user_email.slug  # URL-safe id for paths/indexes
>>> Email("invalid")  # ValidationError
"""

from __future__ import annotations

import re
from typing import Any

from attributes.signature import Signature
from attributes.slug import Slug
from exceptions import ValidationError


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
