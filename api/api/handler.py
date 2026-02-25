"""
API handler: route request path and method to Query/Mutation; merge path params and dispatch.
"""

from __future__ import annotations

from typing import Any

from exceptions import MethodNotAllowedError
from models import User

from api.api.private import private
from api.api.interceptor import interceptor
from api.api.request import ApiRequest
from api.api.urls import URLS
from enums import Method


@interceptor
@private
def handler(request: ApiRequest, context: Any) -> dict[str, Any]:
    """
    Matches request path to route patterns with path parameters.
    Handles OPTIONS for CORS preflight. Merges path params with body/query (path overrides).
    """
    path: str = request.path.lstrip("/")
    method: Method = Method.parse(request.http_method)
    body: dict[str, Any] = request.body or {}
    path_params: dict[str, str] = request.path_params or {}
    query_params: dict[str, str] = request.query_params or {}
    user: User = request.user

    if method == Method.OPTIONS:
        return {}

    handler_class: type | None = None
    matched_prefix: str | None = None
    for url, methods in URLS.items():
        if path.startswith(url):
            handler_class = methods.get(method)
            matched_prefix = url
            break
    if handler_class is None or matched_prefix is None:
        raise MethodNotAllowedError("Method not allowed")

    if not path_params and matched_prefix.endswith("/") and path != matched_prefix.rstrip("/"):
        suffix = path[len(matched_prefix):].strip("/")
        if suffix and "/" not in suffix:
            path_params = {"id": suffix}

    if method == Method.GET:
        merged_data = {**query_params, **path_params}
    else:
        merged_data = {**body, **path_params}

    return handler_class(user=user).handle(body=merged_data)
