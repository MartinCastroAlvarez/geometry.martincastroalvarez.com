"""
Url type: string validated as a valid URL format.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import ParseResult
from urllib.parse import urlparse

from exceptions import ValidationError


class Url(str):
    """
    A string that must be a valid URL (with scheme and netloc). Raises ValidationError (400) if invalid.

    Example:
    >>> u = Url("https://example.com/path")
    >>> Url("not-a-url")  # raises ValidationError
    """

    def __new__(cls, value: Any = None) -> Url:
        if value is None:
            raise ValidationError("Url is required")
        if not isinstance(value, str):
            raise ValidationError("Url must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Url must be a non-empty string")
        parsed: ParseResult = urlparse(raw)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("Url must be a valid URL with scheme and host")
        if parsed.scheme not in ("http", "https", "ftp", "mailto"):
            raise ValidationError("Url scheme must be one of: http, https, ftp, mailto")
        return super().__new__(cls, raw)
