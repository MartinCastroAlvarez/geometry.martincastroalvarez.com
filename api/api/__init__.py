"""
API Gateway Lambda handler package.

Title
-----
API Gateway Handler Package

Context
-------
This package implements the HTTP API surface for the geometry (art gallery)
backend. The handler receives API Gateway proxy events, parses them into
ApiRequest, applies the private (auth) decorator, matches path and method
to URLS, and delegates to Query or Mutation classes. The interceptor wraps
the handler to build ApiResponse with CORS headers and to turn exceptions
into JSON error bodies. Request and response types are used for typing and
serialization. URLS maps path prefixes and HTTP methods to handler classes.

Examples:
>>> from api.api import handler, ApiRequest, ApiResponse, URLS
>>> response_dict = handler(api_gateway_event, context)
"""

from api.api.handler import handler
from api.api.interceptor import interceptor
from api.api.private import private
from api.api.request import ApiRequest
from api.api.response import ApiResponse
from api.api.urls import URLS

__all__ = [
    "ApiRequest",
    "ApiResponse",
    "URLS",
    "handler",
    "interceptor",
    "private",
]
