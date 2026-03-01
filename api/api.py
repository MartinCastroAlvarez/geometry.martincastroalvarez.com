"""
API Gateway Lambda handler: request/response, routing, auth, and entry point.

Title
-----
API Gateway Handler Module

Context
-------
This module implements the HTTP API surface for the geometry (art gallery)
backend. The handler receives API Gateway proxy events, parses them into
ApiRequest, applies the private (auth) decorator, matches path and method
to ROUTES, and delegates to Query or Mutation classes. The interceptor wraps
the handler to build ApiResponse with CORS headers and to turn exceptions
into JSON error bodies. ROUTES maps path prefixes and HTTP methods to handler classes.

Examples:
>>> from api import handler, ApiRequest, ApiResponse, ROUTES
>>> response_dict = handler(api_gateway_event, context)
"""

from __future__ import annotations

import http
import json
import secrets
import time
from functools import wraps
from typing import Any
from typing import Callable
from typing import Type

import jwt
from attributes import Email
from attributes import Origin
from attributes import Path
from controllers import Controller
from controllers import PrivateControllerMixin
from data import Secret
from enums import Method
from exceptions import AuthHeaderRequiredError
from exceptions import ConfigurationError
from exceptions import GeometryException
from exceptions import InternalServerError
from exceptions import InvalidTokenError
from exceptions import MethodNotAllowedError
from exceptions import PathMissingResourceIdError
from exceptions import TokenExpiredError
from exceptions import TokenMissingEmailClaimError
from interfaces import Serializable
from logger import get_logger
from logger import log_extra
from models import User
from mutations import ArtGalleryPublishMutation
from mutations import JobDeleteMutation
from mutations import JobMutation
from mutations import JobUpdateMutation
from queries import ArtGalleryDetailsQuery
from queries import ArtGalleryListQuery
from queries import JobDetailsQuery
from queries import JobListQuery
from settings import JWT_ALGORITHM
from settings import JWT_SECRET_NAME
from settings import JWT_TEST_NAME
from settings import X_AUTH_HEADER
from validations import PolygonValidation

logger = get_logger(__name__)


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


class ApiResponse(Serializable[dict[str, Any]]):
    """
    API Gateway HTTP response with CORS headers.
    Use unserialize(exception) for error responses. Set response.origin before serialize() if needed.
    """

    def __init__(
        self,
        status_code: http.HTTPStatus,
        body: str,
        origin: Origin | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.body = body
        self.origin = origin if origin is not None else Origin()
        self.headers = headers or {}

    def serialize(self) -> dict[str, Any]:
        return {
            "statusCode": self.status_code.value,
            "body": self.body,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": str(self.origin),
                "Access-Control-Allow-Headers": f"Content-Type,X-Amz-Date,Authorization,{X_AUTH_HEADER},X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
                **self.headers,
            },
        }

    @classmethod
    def unserialize(cls, data: Exception) -> ApiResponse:
        if isinstance(data, dict):
            raise NotImplementedError("ApiResponse.unserialize does not support dict")
        if isinstance(data, Exception):
            code = getattr(data, "code", http.HTTPStatus.INTERNAL_SERVER_ERROR)
            status_code = code if isinstance(code, http.HTTPStatus) else http.HTTPStatus(int(code))
            error_type = data.__class__.__name__
            error_message = str(data) if str(data) else "An error occurred"
            body = json.dumps({"error": {"code": status_code.value, "type": error_type, "message": error_message}})
            return cls(status_code=status_code, body=body)
        raise NotImplementedError


ROUTES: dict[Path, dict[Method, Type[Controller]]] = {
    Path("v1/galleries/"): {Method.GET: ArtGalleryDetailsQuery},
    Path("v1/galleries"): {Method.GET: ArtGalleryListQuery},
    Path("v1/polygon"): {Method.POST: PolygonValidation},
    Path("v1/jobs/"): {
        Method.GET: JobDetailsQuery,
        Method.POST: ArtGalleryPublishMutation,
        Method.PATCH: JobUpdateMutation,
        Method.DELETE: JobDeleteMutation,
    },
    Path("v1/jobs"): {Method.GET: JobListQuery, Method.POST: JobMutation},
}


def private(func: Callable) -> Callable:
    """
    Decorator that enforces authentication on handler functions.
    Validates X-Auth header (test token or JWT) and injects User into request.
    """

    @wraps(func)
    def wrapper(request: ApiRequest, *args: Any, **kwargs: Any) -> dict[str, Any]:
        if request.http_method.upper() != Method.OPTIONS.value:
            jwt_secret = Secret.get(JWT_SECRET_NAME)
            jwt_test = Secret.get(JWT_TEST_NAME)
            token: str | None = request.headers.get(X_AUTH_HEADER.lower()) or request.headers.get(X_AUTH_HEADER)
            if not token:
                logger.warning("private.wrapper() | auth failed %s header missing path=%s", X_AUTH_HEADER, request.path)
                raise AuthHeaderRequiredError(f"{X_AUTH_HEADER} header is required")
            if secrets.compare_digest(token, jwt_test):
                request.user = User.test()
            else:
                try:
                    payload = jwt.decode(token, jwt_secret, algorithms=[JWT_ALGORITHM])
                except jwt.ExpiredSignatureError:
                    logger.warning("private.wrapper() | auth failed token expired path=%s", request.path)
                    raise TokenExpiredError("Token has expired")
                except jwt.InvalidTokenError:
                    logger.warning("private.wrapper() | auth failed invalid token path=%s", request.path)
                    raise InvalidTokenError("Invalid token")
                email_raw = payload.get("email")
                if not email_raw:
                    logger.warning("private.wrapper() | auth failed token missing email claim path=%s", request.path)
                    raise TokenMissingEmailClaimError("Token missing email claim")
                email = Email(email_raw)
                request.user = User(
                    email=email,
                    name=payload.get("name", ""),
                    avatar_url=payload.get("avatarUrl"),
                )
        return func(request, *args, **kwargs)

    return wrapper


def interceptor(
    func: Callable[[ApiRequest, Any], dict[str, Any]],
) -> Callable[[dict[str, Any], Any], dict[str, Any]]:
    """
    Decorator: event -> ApiRequest, call handler, return API Gateway response dict.
    Handles GeometryException and generic exceptions; logs request and errors.
    """

    @wraps(func)
    def wrapper(event: dict[str, Any], context: Any) -> dict[str, Any]:
        request_id: str = event.get("requestContext", {}).get("requestId") or getattr(context, "aws_request_id", None) or ""
        path: str = event.get("path", "")
        method: str = event.get("httpMethod", "")
        extra: dict[str, Any] = log_extra(request_id=request_id, path=path, method=method)

        logger.info(
            "Interceptor.wrapper() | request received path=%s method=%s request_id=%s",
            path,
            method,
            request_id,
            extra=extra,
        )
        start: float = time.perf_counter()

        def _request_origin(ev: dict[str, Any]) -> Origin:
            headers = ev.get("headers") or {}
            origin_val = headers.get("Origin") or headers.get("origin")
            if origin_val is None:
                for k, v in headers.items():
                    if k.lower() == "origin" and v:
                        origin_val = v
                        break
            return Origin(origin_val)

        try:
            request: ApiRequest = ApiRequest.unserialize(event)
            result: dict[str, Any] = func(request, context)

            if not isinstance(result, dict):
                raise TypeError(f"Handler must return a dict, got {type(result)}")

            elapsed_ms: float = (time.perf_counter() - start) * 1000
            logger.info(
                "Interceptor.wrapper() | request completed path=%s method=%s status=200 elapsed_ms=%.2f",
                path,
                method,
                elapsed_ms,
                extra={**extra, "elapsed_ms": elapsed_ms, "status": 200},
            )

            origin: Origin = _request_origin(event)
            return ApiResponse(http.HTTPStatus.OK, json.dumps(result), origin).serialize()

        except GeometryException as e:
            elapsed_ms: float = (time.perf_counter() - start) * 1000
            logger.warning(
                "Interceptor.wrapper() | request error path=%s method=%s error=%s code=%s elapsed_ms=%.2f",
                path,
                method,
                str(e),
                getattr(e, "code", 500),
                elapsed_ms,
                extra={**extra, "elapsed_ms": elapsed_ms, "error": str(e)},
            )
            origin = _request_origin(event)
            # Do not expose configuration or internal details to the client.
            if type(e) is ConfigurationError:
                response = ApiResponse.unserialize(InternalServerError("An error occurred"))
            else:
                response = ApiResponse.unserialize(e)
            response.origin = origin
            return response.serialize()

        except Exception as e:
            elapsed_ms: float = (time.perf_counter() - start) * 1000
            logger.exception(
                "Interceptor.wrapper() | request failed path=%s method=%s error=%s elapsed_ms=%.2f",
                path,
                method,
                str(e),
                elapsed_ms,
                extra={**extra, "elapsed_ms": elapsed_ms},
            )
            origin = _request_origin(event)
            # Do not leak internal details (S3, SQS, stack traces); return generic error.
            response = ApiResponse.unserialize(InternalServerError("An error occurred"))
            response.origin = origin
            return response.serialize()

    return wrapper


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
    controller_class: type[Controller] | None = None
    for route_path, methods in ROUTES.items():
        if path.startswith(route_path):
            controller_class = methods.get(method)
            matched_prefix = str(route_path)
            break
    if controller_class is None or matched_prefix is None:
        logger.warning("handler.handler() | method not allowed path=%s method=%s", path, method)
        raise MethodNotAllowedError("Method not allowed")

    logger.debug("handler.handler() | route matched path=%s prefix=%s controller=%s", path, matched_prefix, controller_class.__name__)

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

    if issubclass(controller_class, PrivateControllerMixin):
        instance = controller_class(user=user)
    else:
        instance = controller_class()
    logger.debug("handler.handler() | dispatching controller=%s", controller_class.__name__)
    return instance.handler(body=merged_data)
