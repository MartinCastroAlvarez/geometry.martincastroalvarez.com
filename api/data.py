"""
Data layer: S3 bucket, pagination page, and secrets.

Title
-----
Data Module (Storage and Secrets)

Context
-------
This module provides storage and configuration access for the geometry API.
Bucket wraps S3 for the data bucket (DATA_BUCKET_NAME): load/save/delete
JSON objects by key, and search with prefix and pagination (Page). Page
holds keys and next_token from list_objects_v2. Secret reads secret values
from S3 (SECRETS_BUCKET_NAME). All raise appropriate exceptions on missing env,
S3 errors, or invalid input.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Iterator
from typing import NotRequired
from typing import TypedDict

import boto3
from attributes import Limit
from attributes import Offset
from botocore.exceptions import ClientError
from exceptions import ConfigurationError
from exceptions import NotFoundError
from exceptions import ServiceUnavailableError
from exceptions import StorageError
from exceptions import ValidationError
from logger import get_logger
from settings import DATA_BUCKET_NAME
from settings import DEFAULT_LIMIT
from settings import JWT_SECRET_NAME
from settings import JWT_TEST_NAME
from settings import SECRETS_BUCKET_NAME

logger = get_logger(__name__)


class ListObjectsV2Entry(TypedDict):
    """Single entry in ListObjectsV2Response Contents."""

    Key: str
    LastModified: NotRequired[str]
    ETag: NotRequired[str]
    Size: NotRequired[int]
    StorageClass: NotRequired[str]


class ListObjectsV2Response(TypedDict):
    """Response shape from S3 list_objects_v2. Used for typing in bucket.search()."""

    Contents: list[ListObjectsV2Entry]
    IsTruncated: bool
    NextContinuationToken: str
    KeyCount: int
    MaxKeys: int
    Name: str
    Prefix: str


@dataclass
class Page:
    """
    A page of search results from S3 with pagination support.

    For example, to iterate over keys and check for more pages:
    >>> page = bucket.search(prefix="data/galleries/", limit=20)
    >>> for key in page:
    ...     data = bucket.load(key)
    >>> if page.continues:
    ...     next_page = bucket.search(prefix="...", next_token=page.next_token)
    """

    keys: list[str] = field(default_factory=list)
    next_token: Offset | None = None

    @property
    def continues(self) -> bool:
        """True if there are more pages (next_token is set)."""
        return bool(self.next_token)

    def __len__(self) -> int:
        return len(self.keys)

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys)


@dataclass
class Bucket:
    """
    S3 bucket operations. Bucket name from DATA_BUCKET_NAME env.

    For example, to load and save JSON by key:
    >>> bucket = Bucket()
    >>> data = bucket.load("data/galleries/g1.json")
    >>> bucket.save("data/galleries/g1.json", {"id": "g1", ...})
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
        """
        Return True if the key exists in the bucket.

        For example, to check before loading:
        >>> if bucket.exists("data/galleries/g1.json"):
        ...     data = bucket.load("data/galleries/g1.json")
        """
        if not key or not isinstance(key, str):
            raise ValidationError("Key must be a non-empty string")
        try:
            self.client.head_object(Bucket=self.name, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logger.error("Bucket.exists() | head_object failed key=%s error=%s", key, str(e))
            raise ServiceUnavailableError(f"S3 service error: {str(e)}") from e

    def load(self, key: str, default: Any = None) -> Any:
        """
        Load JSON from key. Returns default if key not found (and default is not None).

        For example, to load a record or get None:
        >>> data = bucket.load("data/galleries/g1.json")
        >>> data = bucket.load("missing.json", default=None)
        """
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
            logger.error("Bucket.load() | get_object failed key=%s error=%s", key, str(e))
            raise ServiceUnavailableError(f"S3 service error: {str(e)}") from e
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON content in object {key}: {str(e)}") from e
        except UnicodeDecodeError as e:
            raise ValidationError(f"Invalid UTF-8 content in object {key}: {str(e)}") from e

    def save(self, key: str, data: Any) -> None:
        """
        Save data as JSON at key. Raises on serialization or S3 errors.

        For example, to persist a gallery:
        >>> bucket.save("data/galleries/g1.json", gallery.serialize())
        """
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
            logger.error("Bucket.save() | put_object failed key=%s error=%s", key, str(e))
            raise ServiceUnavailableError(f"S3 service error: {str(e)}") from e

    def delete(self, key: str) -> bool:
        """
        Delete the object at key. Returns True if deleted, False if key did not exist.

        For example, to remove a record:
        >>> bucket.delete("data/galleries/g1.json")
        True
        """
        if not key or not isinstance(key, str):
            raise ValidationError("Key must be a non-empty string")
        try:
            self.client.delete_object(Bucket=self.name, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return False
            logger.error("Bucket.delete() | delete_object failed key=%s error=%s", key, str(e))
            raise ServiceUnavailableError(f"S3 service error: {str(e)}") from e

    def search(
        self,
        prefix: str = "",
        limit: Limit | int = DEFAULT_LIMIT,
        next_token: Offset | None = None,
    ) -> Page:
        """
        List keys under prefix with pagination; returns Page with keys and next_token.

        For example, to list gallery keys with pagination:
        >>> page = bucket.search(prefix="data/galleries/", limit=20)
        >>> list(page.keys)[:5]
        ['data/galleries/g1.json', ...]
        >>> page.next_token
        Offset('...') or None
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
            logger.error("Bucket.search() | list_objects_v2 failed prefix=%s error=%s", prefix, str(e))
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


class Secret:
    """
    Retrieve secret values from S3. Cached per Lambda execution.

    For example, to get the JWT secret:
    >>> secret = Secret.get(Secret.JWT_SECRET_NAME)
    >>> len(secret) > 0
    True
    """

    JWT_SECRET_NAME: str = JWT_SECRET_NAME
    JWT_TEST_NAME: str = JWT_TEST_NAME

    _client: Any = None
    _cache: dict[str, str] = {}

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
        """
        Get secret value by id. Cached; raises NotFoundError if missing.

        For example, to read the JWT secret:
        >>> jwt_secret = Secret.get("JWT_SECRET")
        """
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
