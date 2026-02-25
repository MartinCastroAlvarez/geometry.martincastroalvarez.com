"""
Typed structures for S3 API responses. Used to type list_objects_v2 and related responses.
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


class ListObjectsV2Response(TypedDict, total=False):
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
