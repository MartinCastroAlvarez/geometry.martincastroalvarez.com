"""
Request: API Gateway event parsing; path, method, headers, body, path_params, query_params, user.
"""

from __future__ import annotations

import json
from typing import Any

from models import User


class Request:
    """
    API Gateway HTTP request parsing and access to request data.

    For example, to parse an API Gateway event:
    >>> event = {'path': '/v1/galleries', 'httpMethod': 'GET', 'headers': {'Content-Type': 'application/json'}}
    >>> request = Request(event)
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

    @classmethod
    def from_dict(cls, event: dict[str, Any]) -> Request:
        return cls(event)

    @property
    def body(self) -> dict[str, Any]:
        if not self._body:
            return {}
        try:
            return json.loads(self._body)
        except json.JSONDecodeError:
            return {}
