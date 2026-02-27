"""
API handler: route request path and method to Query/Mutation; merge path params and dispatch.

Title
-----
API Gateway Request Handler

Context
-------
The handler is the main entry point after the interceptor and private
decorator. It parses the request path (Path), HTTP method (Method), and
merges path parameters with body (POST/PATCH/DELETE) or query params (GET).
Route matching is prefix-based using URLS; the longest matching prefix
wins. For resource-by-id routes (e.g. v1/jobs/), the path's id is extracted
and merged so handlers receive a single "id" in the body. PrivateQuery
and PrivateMutation receive the authenticated User; public handlers get
a default instance. OPTIONS is handled for CORS and returns an empty dict.

Examples:
>>> handler(request, context)  # called by interceptor after ApiRequest is built
>>> # URLS: Path("v1/jobs") -> {Method.GET: JobListQuery, Method.POST: JobMutation}
"""

from __future__ import annotations

from typing import Any

from attributes import Path
from enums import Method
from exceptions import MethodNotAllowedError
from exceptions import PathMissingResourceIdError
from models import User
from mutations.private import PrivateMutation
from queries.private import PrivateQuery

from api.api.interceptor import interceptor
from api.api.private import private
from api.api.request import ApiRequest
from api.api.urls import URLS
from api.logger import get_logger

logger = get_logger(__name__)


@interceptor
@private
def handler(request: ApiRequest, context: Any) -> dict[str, Any]:
    """
    Matches request path to route patterns with path parameters.
    Handles OPTIONS for CORS preflight. Merges path params with body/query (path overrides).
    """
    path: Path = request.path
    method: Method = Method.parse(request.http_method)
    body: dict[str, Any] = request.body or {}
    path_params: dict[str, str] = dict(request.path_params or {})
    query_params: dict[str, str] = request.query_params or {}
    user: User = request.user

    if method == Method.OPTIONS:
        return {}

    matched_prefix: str | None = None
    for route_path, methods in URLS.items():
        if path.startswith(route_path):
            handler_class = methods.get(method)
            matched_prefix = str(route_path)
            break
    if handler_class is None or matched_prefix is None:
        logger.warning("handler.handler() | method not allowed path=%s method=%s", path, method)
        raise MethodNotAllowedError("Method not allowed")

    logger.debug("handler.handler() | route matched path=%s prefix=%s handler=%s", path, matched_prefix, handler_class.__name__)

    if not path_params and matched_prefix.endswith("/") and path != matched_prefix.rstrip("/"):
        try:
            path_params = {"id": path.id}
        except PathMissingResourceIdError:
            pass

    merged_data: dict[str, Any]
    if method == Method.GET:
        merged_data = {**query_params, **path_params}
    else:
        merged_data = {**body, **path_params}

    if issubclass(handler_class, (PrivateQuery, PrivateMutation)):
        instance = handler_class(user=user)
    else:
        instance = handler_class()
    logger.debug("handler.handler() | dispatching handler=%s", handler_class.__name__)
    return instance.handle(body=merged_data)
