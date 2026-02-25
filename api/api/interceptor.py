"""
interceptor: decorator that wraps event -> Request, calls handler, returns response dict; catches exceptions.
"""

from __future__ import annotations

import json
import logging
from functools import wraps
from typing import Any
from typing import Callable

from api.api.request import Request
from api.api.response import Response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def interceptor(func: Callable) -> Callable:
    """
    Decorator for Lambda handler functions: event -> Request, call handler, return response dict.
    Exceptions are converted to error responses. Handler must return a dict.
    """

    @wraps(func)
    def wrapper(event: dict[str, Any], context: Any) -> dict[str, Any]:
        try:
            request = Request.from_dict(event)
            result = func(request, context)
            if not isinstance(result, dict):
                raise TypeError(f"Handler must return a dict, got {type(result)}")
            response = Response(200, json.dumps(result))
            origin = request.headers.get("Origin") or request.headers.get("origin")
            return response.to_dict(request_origin=origin)
        except Exception as e:
            logger.exception("Error in handler %s: %s", func.__name__, e)
            error_response = Response.from_error(e)
            origin = event.get("headers", {}).get("Origin") or event.get("headers", {}).get("origin")
            return error_response.to_dict(request_origin=origin)

    return wrapper
