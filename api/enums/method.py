"""
Method enum for HTTP request methods: OPTIONS, GET, POST, PATCH, DELETE.

Title
-----
HTTP Method Enum

Context
-------
Method represents the HTTP verb of a request. Values are OPTIONS, GET,
POST, PATCH, DELETE. parse(value) coerces a string to Method; None or
empty raises MethodNotAllowedError; invalid value raises with allowed list.
Used by the API handler to dispatch by method and by URLS (Path -> Method -> Handler).
OPTIONS is used for CORS preflight and is handled without auth.

Examples:
    method = Method.parse(request.http_method)
    handler_class = URLS[path_prefix].get(method)
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
