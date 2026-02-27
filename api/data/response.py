"""
Typed structures for S3 API responses.

Title
-----
S3 Response Types

Context
-------
This module defines TypedDicts for S3 API responses used by the data layer.
ListObjectsV2Entry describes a single object in the Contents list (Key and
optional LastModified, ETag, Size, StorageClass). ListObjectsV2Response
describes the full list_objects_v2 response (Contents, IsTruncated,
NextContinuationToken, etc.). Used in bucket.search() to type the boto3
response and validate shape; invalid or non-dict response is handled with
StorageError. Keeps S3 contract explicit and documentable.

Examples:
    response: ListObjectsV2Response = client.list_objects_v2(...)
    for obj in response.get("Contents", []):
        keys.append(obj["Key"])
    next_token = response.get("NextContinuationToken", "")
"""

from __future__ import annotations

from typing import NotRequired
from typing import TypedDict


class ListObjectsV2Entry(TypedDict):
    """Single entry in ListObjectsV2Response Contents."""

    Key: str
    LastModified: NotRequired[str]
    ETag: NotRequired[str]
    Size: NotRequired[int]
    StorageClass: NotRequired[str]


class ListObjectsV2Response(TypedDict):
    """
    Response shape from S3 list_objects_v2. Used for typing in bucket.search().

    Contents and NextContinuationToken are optional (absent when empty/not truncated).
    """

    Contents: list[ListObjectsV2Entry]
    IsTruncated: bool
    NextContinuationToken: str
    KeyCount: int
    MaxKeys: int
    Name: str
    Prefix: str
