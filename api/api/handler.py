"""
API handler: route request path and method to Query/Mutation; merge path params and dispatch.
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
