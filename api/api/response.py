"""
ApiResponse: API Gateway response formatting with CORS.
"""

from __future__ import annotations

import http
import json
from typing import Any

from attributes import Origin
from interfaces import Serializable


class ApiResponse(Serializable[dict[str, Any]]):
    """
    API Gateway HTTP response with CORS headers.
    Use unserialize(exception) for error responses. Set response.origin before serialize() if needed.
    """

    def __init__(
        self,
        status_code: http.HTTPStatus,
        body: str,
        origin: Origin | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.origin = origin if origin is not None else Origin()
        self.headers = headers or {}

    def serialize(self) -> dict[str, Any]:
        return {
            "statusCode": self.status_code.value,
            "body": self.body,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": str(self.origin),
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Auth,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
                **self.headers,
            },
        }

    @classmethod
    def unserialize(cls, data: Exception) -> ApiResponse:
        if isinstance(data, dict):
            raise NotImplementedError("ApiResponse.unserialize does not support dict")
        if isinstance(data, Exception):
            code = getattr(data, "code", http.HTTPStatus.INTERNAL_SERVER_ERROR)
            status_code = code if isinstance(code, http.HTTPStatus) else http.HTTPStatus(int(code))
            error_type = data.__class__.__name__
            error_message = str(data) if str(data) else "An error occurred"
            body = json.dumps({"error": {"code": status_code.value, "type": error_type, "message": error_message}})
            return cls(status_code=status_code, body=body)
        raise NotImplementedError
