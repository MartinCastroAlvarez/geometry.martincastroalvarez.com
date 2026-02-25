"""
Slug type: non-empty string normalized to lowercase, alphanumeric and dashes only.
"""

from __future__ import annotations

import re
from typing import Any

from exceptions import ValidationError


class Slug(str):
    """
    A string slug: validated (not None, non-empty string) and normalized to
    lowercase with non-alphanumeric replaced by a single dash, stripped.

    Example:
    >>> s = Slug("User@Example.com")
    >>> str(s)
    'user-example-com'
    >>> Slug("  hello  world  ")
    'hello-world'
    """

    def __new__(cls, value: Any) -> Slug:
        if value is None:
            raise ValidationError("Slug is required")
        if not isinstance(value, str):
            raise ValidationError("Slug must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Slug must be a non-empty string")
        lower: str = raw.lower()
        normalized: str = re.sub(r"[^a-z0-9]+", "-", lower).strip("-") or "x"
        return super().__new__(cls, normalized)
