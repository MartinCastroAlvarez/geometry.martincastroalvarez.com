"""
Configuration and constants from environment.

Title
-----
Settings Module

Context
-------
Central place for values read from the environment and for named constants
used across the API (e.g. secret names, bucket names, default pagination).
All env-backed values are read at import time. Tests can set os.environ
before importing (e.g. in conftest) to override.

Examples:
>>> from settings import DATA_BUCKET_NAME, DEFAULT_LIMIT
>>> from settings import JWT_SECRET_NAME
"""

from __future__ import annotations

import os

from enums import LogLevel

DATA_BUCKET_NAME: str | None = os.getenv("DATA_BUCKET_NAME")
SECRETS_BUCKET_NAME: str | None = os.getenv("SECRETS_BUCKET_NAME")
QUEUE_NAME: str | None = os.getenv("QUEUE_NAME")

DEBUG: bool = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")
LOG_LEVEL: LogLevel = LogLevel.DEBUG if DEBUG else LogLevel.parse(os.getenv("LOG_LEVEL", "INFO") or "INFO")

# When True, 500 error responses include a "traceback" field (for debugging only).
EXPOSE_TRACEBACK: bool = os.getenv("EXPOSE_TRACEBACK", "").lower() in ("1", "true", "yes")

JWT_SECRET_NAME: str = "JWT_SECRET"
JWT_TEST_NAME: str = "JWT_TEST"
JWT_ALGORITHM: str = "HS256"

# Request header for auth (use .lower() for case-insensitive lookup)
X_AUTH_HEADER: str = "X-Auth"

DEFAULT_LIMIT: int = int(os.getenv("DEFAULT_LIMIT", "20"))
MAX_LIMIT: int = int(os.getenv("MAX_LIMIT", "1000"))

# Title length (User name, gallery title, etc.)
DEFAULT_TITLE_MAX_LENGTH: int = int(os.getenv("DEFAULT_TITLE_MAX_LENGTH", "200"))

# Default gallery title when none is provided
UNTITLED_ART_GALLERY_NAME: str = "Untitled Art Gallery"

# SQS receive (SQS API: MaxNumberOfMessages 1–10, WaitTimeSeconds 0–20)
QUEUE_WAIT_TIME_SECONDS: int = int(os.getenv("QUEUE_WAIT_TIME_SECONDS", "20"))
QUEUE_WAIT_TIME_SECONDS_MAX: int = int(os.getenv("QUEUE_WAIT_TIME_SECONDS_MAX", "20"))
QUEUE_MAX_RECEIVE_MESSAGES: int = int(os.getenv("QUEUE_MAX_RECEIVE_MESSAGES", "10"))

# CORS / origin fallback when request origin is not in allowed list
DEFAULT_ORIGIN: str = os.getenv("DEFAULT_ORIGIN") or "https://geometry.martincastroalvarez.com"

# Anonymous and test user constants (used by User model)
ANONYMOUS_EMAIL: str = "nobody@unknown.local"
ANONYMOUS_NAME: str = "Anonymous"
ANONYMOUS_AVATAR_URL: str = "https://picsum.photos/200"
TEST_EMAIL: str = "test@test.com"
TEST_NAME: str = "test test"
TEST_AVATAR_URL: str = "https://picsum.photos/200"
