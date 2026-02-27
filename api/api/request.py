"""
ApiRequest: API Gateway event parsing; path, method, headers, body, path_params, query_params, user.

Title
-----
API Gateway Request Model

Context
-------
ApiRequest parses the API Gateway proxy integration event into a typed
object. The path is normalized (no leading slash) and wrapped as Path.
Headers, queryStringParameters, and pathParameters are exposed as dicts.
The body is JSON-decoded; if missing or invalid, body is {}. The user
starts as anonymous and is set by the private decorator when X-Auth is
valid. Implementations use ApiRequest.unserialize(event) to build the
request before passing it to the handler. This type is used across the
api.api package and by Query/Mutation code that receives the request.

Examples:
    request = ApiRequest.unserialize(event)
    path, method = request.path, request.http_method
    user = request.user
    body = request.body
"""

from __future__ import annotations

import json
from typing import Any

from attributes import Path
from interfaces import Serializable
from models import User


class ApiRequest(Serializable[dict[str, Any]]):
    """
    API Gateway HTTP request parsing and access to request data.

    For example, to parse an API Gateway event:
    >>> event = {'path': '/v1/galleries', 'httpMethod': 'GET', 'headers': {'Content-Type': 'application/json'}}
    >>> request = ApiRequest.unserialize(event)
    >>> request.path
    'v1/galleries'
    >>> request.http_method
    'GET'
    >>> request.body
    {}
    >>> request.user
    User(email='', name='', avatar_url=None)
    """

    def __init__(self, event: dict[str, Any]) -> None:
        self.event: dict[str, Any] = event
        self.path: Path = Path(event.get("path", ""))
        self.http_method: str = event.get("httpMethod", "")
        self.headers: dict[str, str] = event.get("headers", {}) or {}
        self.query_params: dict[str, str] = event.get("queryStringParameters") or {}
        self.path_params: dict[str, str] = event.get("pathParameters") or {}
        self._body: str = event.get("body", "")
        self.is_base64_encoded: bool = event.get("isBase64Encoded", False)
        self.user: User = User.anonymous()

    def serialize(self) -> dict[str, Any]:
        raise NotImplementedError("ApiRequest.serialize is not used")

    @classmethod
    def unserialize(cls, event: dict[str, Any]) -> ApiRequest:
        return cls(event)

    @property
    def body(self) -> dict[str, Any]:
        if not self._body:
            return {}
        try:
            return json.loads(self._body)
        except json.JSONDecodeError:
            return {}
