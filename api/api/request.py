"""
ApiRequest: API Gateway event parsing; path, method, headers, body, path_params, query_params, user.
"""

from __future__ import annotations

import json
from typing import Any

from interfaces import Serializable
from models import User


class ApiRequest(Serializable[dict[str, Any]]):
    """
    API Gateway HTTP request parsing and access to request data.

    For example, to parse an API Gateway event:
    >>> event = {'path': '/v1/galleries', 'httpMethod': 'GET', 'headers': {'Content-Type': 'application/json'}}
    >>> request = ApiRequest.unserialize(event)
    >>> request.path
    '/v1/galleries'
    >>> request.http_method
    'GET'
    >>> request.body
    {}
    >>> request.user
    User(email='', name='', avatar_url=None)
    """

    def __init__(self, event: dict[str, Any]) -> None:
        self.event: dict[str, Any] = event
        self.path: str = event.get("path", "")
        self.http_method: str = event.get("httpMethod", "")
        self.headers: dict[str, str] = event.get("headers", {}) or {}
        self.query_params: dict[str, str] = event.get("queryStringParameters") or {}
        self.path_params: dict[str, str] = event.get("pathParameters") or {}
        self._body: str = event.get("body", "")
        self.is_base64_encoded: bool = event.get("isBase64Encoded", False)
        self.user: User = User()

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
