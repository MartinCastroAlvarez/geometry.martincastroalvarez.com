"""
Access to secrets stored in S3 for the geometry API.
"""

from __future__ import annotations

import os
from typing import Any
from typing import ClassVar

import boto3
from botocore.exceptions import ClientError

from exceptions import (
    ConfigurationError,
    NotFoundError,
    ServiceUnavailableError,
    ValidationError,
)

SECRETS_BUCKET_NAME: str | None = os.getenv("SECRETS_BUCKET_NAME")


class Secret:
    """
    Retrieve secret values from S3. Cached per Lambda execution.

    Example:
    >>> secret = Secret.get(Secret.JWT_SECRET_NAME)
    >>> test_token = Secret.get(Secret.JWT_TEST_NAME)
    """

    JWT_SECRET_NAME: ClassVar[str] = "JWT_SECRET"
    JWT_TEST_NAME: ClassVar[str] = "JWT_TEST"

    _client: ClassVar[Any] = None
    _cache: ClassVar[dict[str, str]] = {}

    @classmethod
    def _get_client(cls) -> Any:
        if cls._client is None:
            cls._client = boto3.client("s3")
        return cls._client

    @classmethod
    def _get_bucket_name(cls) -> str:
        if not SECRETS_BUCKET_NAME:
            raise ConfigurationError("SECRETS_BUCKET_NAME environment variable is required")
        return SECRETS_BUCKET_NAME

    @classmethod
    def get(cls, secret_id: str) -> str:
        if not secret_id or not isinstance(secret_id, str):
            raise ValidationError("Secret ID must be a non-empty string")
        if secret_id in cls._cache:
            return cls._cache[secret_id]
        bucket_name = cls._get_bucket_name()
        client = cls._get_client()
        try:
            response: Any = client.get_object(Bucket=bucket_name, Key=secret_id)
            content: str = response["Body"].read().decode("utf-8").strip()
            if not content:
                raise NotFoundError(f"Secret '{secret_id}' is empty")
            cls._cache[secret_id] = content
            return content
        except ClientError as err:
            if err.response["Error"]["Code"] == "NoSuchKey":
                raise NotFoundError(f"Secret '{secret_id}' not found")
            raise ServiceUnavailableError(f"S3 service error: {str(err)}") from err
