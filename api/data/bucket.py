"""
S3 bucket operations for the geometry API.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from dataclasses import field
from typing import Any

import boto3
from attributes import Limit
from attributes import Offset
from botocore.exceptions import ClientError
from data.page import Page
from data.response import ListObjectsV2Response
from exceptions import ConfigurationError
from exceptions import ServiceUnavailableError
from exceptions import StorageError
from exceptions import ValidationError

DATA_BUCKET_NAME: str | None = os.getenv("DATA_BUCKET_NAME")


@dataclass
class Bucket:
    """
    S3 bucket operations. Bucket name from DATA_BUCKET_NAME env.

    Example:
    >>> bucket = Bucket()
    >>> bucket.save("data/galleries/abc.json", {"id": "abc", "boundary": []})
    >>> data = bucket.load("data/galleries/abc.json")
    >>> page = bucket.search(prefix="data/galleries/", limit=20, next_token=token)
    """

    _client: Any = field(default=None, init=False, repr=False)

    @property
    def name(self) -> str:
        if not DATA_BUCKET_NAME:
            raise ConfigurationError("DATA_BUCKET_NAME environment variable is required")
        return DATA_BUCKET_NAME

    @property
    def client(self) -> Any:
        if self._client is None:
            self._client = boto3.client("s3")
        return self._client

    def exists(self, key: str) -> bool:
        if not key or not isinstance(key, str):
            raise ValidationError("Key must be a non-empty string")
        try:
            self.client.head_object(Bucket=self.name, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise ServiceUnavailableError(f"S3 service error: {str(e)}") from e

    def load(self, key: str, default: Any = None) -> Any:
        if not key or not isinstance(key, str):
            raise ValidationError("Key must be a non-empty string")
        try:
            response: Any = self.client.get_object(Bucket=self.name, Key=key)
            if "Body" not in response:
                raise ValidationError(f"Invalid S3 response: missing Body for key {key}")
            content: str = response["Body"].read().decode("utf-8")
            if not content.strip():
                raise ValidationError(f"Empty content in S3 object {key}")
            return json.loads(content)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return default
            raise ServiceUnavailableError(f"S3 service error: {str(e)}") from e
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON content in object {key}: {str(e)}") from e
        except UnicodeDecodeError as e:
            raise ValidationError(f"Invalid UTF-8 content in object {key}: {str(e)}") from e

    def save(self, key: str, data: Any) -> None:
        if not key or not isinstance(key, str):
            raise ValidationError("Key must be a non-empty string")
        try:
            json_data: str = json.dumps(data, indent=2)
            self.client.put_object(
                Bucket=self.name,
                Key=key,
                Body=json_data.encode("utf-8"),
                ContentType="application/json",
            )
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Data is not JSON serializable: {str(e)}") from e
        except ClientError as e:
            raise ServiceUnavailableError(f"S3 service error: {str(e)}") from e

    def delete(self, key: str) -> bool:
        if not key or not isinstance(key, str):
            raise ValidationError("Key must be a non-empty string")
        try:
            self.client.delete_object(Bucket=self.name, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return False
            raise ServiceUnavailableError(f"S3 service error: {str(e)}") from e

    def search(
        self,
        prefix: str = "",
        limit: Limit | int = 20,
        next_token: Offset | None = None,
    ) -> Page:
        """
        List keys under prefix with pagination; returns Page with keys and next_token.
        """
        if prefix and not isinstance(prefix, str):
            raise ValidationError("Prefix must be a string")
        size = Limit(limit) if not isinstance(limit, Limit) else limit
        params: dict[str, Any] = {
            "Bucket": self.name,
            "Prefix": prefix,
            "MaxKeys": int(size),
        }
        if next_token is not None:
            params["ContinuationToken"] = str(next_token)
        try:
            response: ListObjectsV2Response = self.client.list_objects_v2(**params)
        except ClientError as e:
            raise ServiceUnavailableError(f"S3 service error: {str(e)}") from e
        if not isinstance(response, dict):
            raise StorageError("Invalid S3 response: expected dictionary")
        keys: list[str] = []
        if "Contents" in response:
            for obj in response["Contents"]:
                keys.append(obj["Key"])
        new_next = ""
        if response.get("IsTruncated", False):
            new_next = response.get("NextContinuationToken") or ""
        return Page(
            keys=keys,
            next_token=Offset(new_next) if new_next else None,
        )
