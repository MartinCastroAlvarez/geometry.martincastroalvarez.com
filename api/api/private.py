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
from data import Secret
from enums import Method
from exceptions import UnauthorizedError
from models import User

from api.api.request import ApiRequest
from api.logger import get_logger

logger = get_logger(__name__)


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
                logger.warning("private.wrapper() | auth failed X-Auth header missing path=%s", request.path)
                raise UnauthorizedError("X-Auth header is required")
            if secrets.compare_digest(token, jwt_test):
                request.user = User.test()
            else:
                try:
                    payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                except jwt.ExpiredSignatureError:
                    logger.warning("private.wrapper() | auth failed token expired path=%s", request.path)
                    raise UnauthorizedError("Token has expired")
                except jwt.InvalidTokenError:
                    logger.warning("private.wrapper() | auth failed invalid token path=%s", request.path)
                    raise UnauthorizedError("Invalid token")
                email_raw = payload.get("email")
                if not email_raw:
                    logger.warning("private.wrapper() | auth failed token missing email claim path=%s", request.path)
                    raise UnauthorizedError("Token missing email claim")
                email = Email(email_raw)
                request.user = User(
                    email=email,
                    name=payload.get("name", ""),
                    avatar_url=payload.get("avatarUrl"),
                )
        return func(request, *args, **kwargs)

    return wrapper
