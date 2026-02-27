"""
Interceptor: converts API Gateway event to ApiRequest, calls handler, formats response.

Title
-----
API Request/Response Interceptor

Context
-------
The interceptor is a decorator that wraps the main handler. It receives
the raw API Gateway event and context, builds ApiRequest via ApiRequest.unserialize(event),
calls the underlying handler(request, context), and converts the returned
dict into an API Gateway response via ApiResponse. It logs each request
(path, method, request_id) and elapsed time; on GeometryException it logs
a warning and returns ApiResponse.unserialize(e).serialize(); on any other
exception it logs the full traceback and returns a 500-style response.
CORS origin is taken from the request Origin header and set on the response.

Examples:
    @interceptor
    @private
    def handler(request: ApiRequest, context) -> dict[str, Any]: ...
    # In Lambda: handler(event, context) receives raw event; interceptor does the rest.
"""

from __future__ import annotations

import http
import json
import time
from functools import wraps
from typing import Any
from typing import Callable

from attributes import Origin
from exceptions import GeometryException

from api.api.request import ApiRequest
from api.api.response import ApiResponse
from api.logger import get_logger
from api.logger import log_extra

logger = get_logger(__name__)


def interceptor(
    func: Callable[[ApiRequest, Any], dict[str, Any]],
) -> Callable[[dict[str, Any], Any], dict[str, Any]]:
    """
    Decorator: event -> ApiRequest, call handler, return API Gateway response dict.
    Handles GeometryException and generic exceptions; logs request and errors.
    """

    @wraps(func)
    def wrapper(event: dict[str, Any], context: Any) -> dict[str, Any]:
        request_id: str = event.get("requestContext", {}).get("requestId") or getattr(context, "aws_request_id", None) or ""
        path: str = event.get("path", "")
        method: str = event.get("httpMethod", "")
        extra: dict[str, Any] = log_extra(request_id=request_id, path=path, method=method)

        logger.info(
            "Interceptor.wrapper() | request received path=%s method=%s request_id=%s",
            path,
            method,
            request_id,
            extra=extra,
        )
        start: float = time.perf_counter()

        try:
            request: ApiRequest = ApiRequest.unserialize(event)
            result: dict[str, Any] = func(request, context)

            if not isinstance(result, dict):
                raise TypeError(f"Handler must return a dict, got {type(result)}")

            elapsed_ms: float = (time.perf_counter() - start) * 1000
            logger.info(
                "Interceptor.wrapper() | request completed path=%s method=%s status=200 elapsed_ms=%.2f",
                path,
                method,
                elapsed_ms,
                extra={**extra, "elapsed_ms": elapsed_ms, "status": 200},
            )

            origin: Origin = Origin(event.get("headers", {}).get("Origin") or event.get("headers", {}).get("origin"))
            return ApiResponse(http.HTTPStatus.OK, json.dumps(result), origin).serialize()

        except GeometryException as e:
            elapsed_ms: float = (time.perf_counter() - start) * 1000
            logger.warning(
                "Interceptor.wrapper() | request error path=%s method=%s error=%s code=%s elapsed_ms=%.2f",
                path,
                method,
                str(e),
                getattr(e, "code", 500),
                elapsed_ms,
                extra={**extra, "elapsed_ms": elapsed_ms, "error": str(e)},
            )
            origin: Origin = Origin(event.get("headers", {}).get("Origin") or event.get("headers", {}).get("origin"))
            response: ApiResponse = ApiResponse.unserialize(e)
            response.origin = origin
            return response.serialize()

        except Exception as e:
            elapsed_ms: float = (time.perf_counter() - start) * 1000
            logger.exception(
                "Interceptor.wrapper() | request failed path=%s method=%s error=%s elapsed_ms=%.2f",
                path,
                method,
                str(e),
                elapsed_ms,
                extra={**extra, "elapsed_ms": elapsed_ms},
            )
            origin: Origin = Origin(event.get("headers", {}).get("Origin") or event.get("headers", {}).get("origin"))
            response: ApiResponse = ApiResponse.unserialize(e)
            response.origin = origin
            return response.serialize()

    return wrapper
