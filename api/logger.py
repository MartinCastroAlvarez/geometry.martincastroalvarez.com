"""
Centralized logging for the geometry API.

Title
-----
Geometry API Logger

Context
-------
Provides structured logging with request_id support for correlation across
API Gateway, Authorizer, and Worker Lambdas. Use get_logger(__name__) in
each module. log_extra() builds a JSON-friendly dict for request_id, path,
method, and custom kwargs so CloudWatch can index and filter logs. Call
configure_logging() at Lambda cold start if you need to set the root log
level from LOG_LEVEL env (default INFO). CloudWatch captures stdout from
the Lambda runtime.

Examples:
    logger = get_logger(__name__)
    logger.info("message", extra=log_extra(request_id=req_id, path=path))
    configure_logging()
"""

from __future__ import annotations

import logging
import os
from typing import Any


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given module name."""
    return logging.getLogger(name)


def log_extra(
    request_id: str | None = None,
    path: str | None = None,
    method: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Build extra dict for structured logging (JSON-compatible).
    Use with logger.info("msg", extra=log_extra(request_id=..., path=...)).
    """
    extra: dict[str, Any] = dict(kwargs)
    if request_id is not None:
        extra["request_id"] = request_id
    if path is not None:
        extra["path"] = path
    if method is not None:
        extra["method"] = method
    return extra


def configure_logging() -> None:
    """
    Configure root logger for Lambda. Call at Lambda cold start if needed.
    CloudWatch captures stdout; Lambda runtime sets log level from env.
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.getLogger().setLevel(getattr(logging, level, logging.INFO))
