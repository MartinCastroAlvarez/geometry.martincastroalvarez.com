"""
Method enum for HTTP request methods: OPTIONS, GET, POST, DELETE.
"""

from __future__ import annotations

from enum import Enum

from exceptions import MethodNotAllowedError


class Method(str, Enum):
    """HTTP method: OPTIONS, GET, POST, PATCH, DELETE."""

    OPTIONS = "OPTIONS"
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"

    @classmethod
    def parse(cls, value: str | None) -> Method:
        """Coerce string to Method; raises MethodNotAllowedError if invalid or missing."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise MethodNotAllowedError("HTTP method is required")
        raw: str = value.strip().upper() if isinstance(value, str) else str(value).strip().upper()
        try:
            return cls(raw)
        except ValueError:
            raise MethodNotAllowedError(
                f"method must be one of [{', '.join(m.value for m in cls)}], got {raw!r}"
            )
