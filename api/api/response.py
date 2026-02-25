"""
Response: status code, body, CORS headers; from_error() builds error responses from exceptions.
"""

from __future__ import annotations

import json
from typing import Any


class Response:
    """
    API Gateway HTTP response formatting with CORS headers.

    For example, to create a successful response:
    >>> response = Response(200, '{"message": "success"}')
    >>> response.status_code
    200
    >>> response_dict = response.to_dict()
    >>> response_dict['statusCode']
    200
    """

    def __init__(
        self,
        status_code: int,
        body: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code: int = status_code
        self.body: str = body
        self.headers: dict[str, str] = headers or {}

    def to_dict(self, request_origin: str | None = None) -> dict[str, Any]:
        cors_origin = self._get_cors_origin(request_origin)
        return {
            "statusCode": self.status_code,
            "body": self.body,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": cors_origin,
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Auth,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
                **self.headers,
            },
        }

    def _get_cors_origin(self, request_origin: str | None) -> str:
        """
        Allowed patterns: https://*.martincastroalvarez.com, http://localhost:*
        """
        if not request_origin:
            return "*"
        if request_origin.startswith("https://") and request_origin.endswith(".martincastroalvarez.com"):
            return request_origin
        if request_origin.startswith("http://localhost:") or request_origin == "http://localhost":
            return request_origin
        return "https://geometry.martincastroalvarez.com"

    @classmethod
    def from_error(cls, exception: Exception) -> Response:
        status_code: int = getattr(exception, "code", 500)
        error_type: str = exception.__class__.__name__
        error_message: str = str(exception) if str(exception) else "An error occurred"
        error_body: dict[str, Any] = {"error": {"code": status_code, "type": error_type, "message": error_message}}
        return cls(status_code=status_code, body=json.dumps(error_body))
