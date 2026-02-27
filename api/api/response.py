"""
ApiResponse: API Gateway response formatting with CORS.

Title
-----
API Gateway Response Model

Context
-------
ApiResponse builds the response shape expected by API Gateway (statusCode,
body, headers). CORS headers (Access-Control-Allow-Origin, etc.) are
included so browsers can call the API from allowed origins. The origin
is taken from the request Origin header and normalized via attributes.Origin;
if unset, use Origin() for default. For success, the interceptor builds
ApiResponse(status_code=200, body=json.dumps(result), origin=...). For
errors, ApiResponse.unserialize(exception) builds a JSON body with
error.code, error.type, and error.message. Handlers return dicts; the
interceptor turns them into ApiResponse and then serialize() for Gateway.

Examples:
>>> response = ApiResponse(http.HTTPStatus.OK, json.dumps(data), origin=Origin())
>>> return response.serialize()
>>> response = ApiResponse.unserialize(ValidationError("bad input"))
>>> response.origin = Origin(request_headers.get("Origin"))
>>> return response.serialize()
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
