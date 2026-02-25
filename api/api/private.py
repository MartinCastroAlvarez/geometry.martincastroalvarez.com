"""
private: decorator that validates X-Auth (test token or JWT) and sets request.user.
"""

from __future__ import annotations

import secrets
from functools import wraps
from typing import Any
from typing import Callable

import jwt

from attributes import Email
from attributes import Identifier
from attributes import Signature
from data import Secret
from exceptions import UnauthorizedError
from models import User

from api.api.request import ApiRequest
from enums import Method


def private(func: Callable) -> Callable:
    """
    Decorator that enforces authentication on handler functions.
    Validates X-Auth header (test token or JWT) and injects User into request.
    """

    @wraps(func)
    def wrapper(request: ApiRequest, *args: Any, **kwargs: Any) -> dict[str, Any]:
        if request.http_method.upper() != Method.OPTIONS.value:
            jwt_secret = Secret.get(Secret.JWT_SECRET_NAME)
            jwt_test = Secret.get(Secret.JWT_TEST_NAME)
            token: str | None = request.headers.get("X-Auth") or request.headers.get("x-auth")
            if not token:
                raise UnauthorizedError("X-Auth header is required")
            if secrets.compare_digest(token, jwt_test):
                test_email = Email(User.TEST_EMAIL)
                request.user = User(
                    id=Identifier(test_email.slug),
                    email=test_email,
                    name=User.TEST_NAME,
                    avatar_url=User.TEST_AVATAR_URL,
                )
            else:
                try:
                    payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                except jwt.ExpiredSignatureError:
                    raise UnauthorizedError("Token has expired")
                except jwt.InvalidTokenError:
                    raise UnauthorizedError("Invalid token")
                email_raw = payload.get("email")
                if not email_raw:
                    raise UnauthorizedError("Token missing email claim")
                email = Email(email_raw)
                request.user = User(
                    id=Identifier(email.slug),
                    email=email,
                    name=payload.get("name", ""),
                    avatar_url=payload.get("avatarUrl"),
                )
        return func(request, *args, **kwargs)

    return wrapper
