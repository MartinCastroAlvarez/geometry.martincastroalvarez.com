"""
interceptor: decorator that wraps event -> ApiRequest, calls handler, returns response dict; catches exceptions.
"""

from __future__ import annotations

import json
import logging
from functools import wraps
from typing import Any
from typing import Callable

from api.api.request import ApiRequest
from api.api.response import ApiResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def interceptor(func: Callable) -> Callable:
    """
    Decorator for Lambda handler functions: event -> ApiRequest, call handler, return response dict.
    Exceptions are converted to error responses. Handler must return a dict.
    """

    @wraps(func)
    def wrapper(event: dict[str, Any], context: Any) -> dict[str, Any]:
        try:
            request = ApiRequest.unserialize(event)
            result = func(request, context)
            if not isinstance(result, dict):
                raise TypeError(f"Handler must return a dict, got {type(result)}")
            response = ApiResponse(200, json.dumps(result))
            origin = request.headers.get("Origin") or request.headers.get("origin")
            return response.serialize(request_origin=origin)
        except Exception as e:
            logger.exception("Error in handler %s: %s", func.__name__, e)
            error_response = ApiResponse.from_error(e)
            origin = event.get("headers", {}).get("Origin") or event.get("headers", {}).get("origin")
            return error_response.serialize(request_origin=origin)

    return wrapper
