"""
private: decorator that validates X-Auth (test token or JWT) and sets request.user.
"""

from __future__ import annotations

import secrets
from functools import wraps
from typing import Any
from typing import Callable

import jwt

from data import Secret
from exceptions import UnauthorizedError
from models import User

from api.api.request import Request


def private(func: Callable) -> Callable:
    """
    Decorator that enforces authentication on handler functions.
    Validates X-Auth header (test token or JWT) and injects User into request.
    """

    @wraps(func)
    def wrapper(request: Request, *args: Any, **kwargs: Any) -> dict[str, Any]:
        if request.http_method.upper() != "OPTIONS":
            jwt_secret = Secret.get("JWT_SECRET")
            jwt_test = Secret.get("JWT_TEST")
            token: str | None = request.headers.get("X-Auth") or request.headers.get("x-auth")
            if not token:
                raise UnauthorizedError("X-Auth header is required")
            if secrets.compare_digest(token, jwt_test):
                request.user = User(
                    id="test@test.com",
                    email="test@test.com",
                    name="test test",
                    avatar_url="https://picsum.photos/200",
                )
            else:
                try:
                    payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                except jwt.ExpiredSignatureError:
                    raise UnauthorizedError("Token has expired")
                except jwt.InvalidTokenError:
                    raise UnauthorizedError("Invalid token")
                email = payload.get("email")
                if not email:
                    raise UnauthorizedError("Token missing email claim")
                request.user = User(
                    id=email,
                    email=email,
                    name=payload.get("name", ""),
                    avatar_url=payload.get("avatarUrl"),
                )
        return func(request, *args, **kwargs)

    return wrapper
