"""
A page of search results from S3 with pagination support.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Iterator

from attributes import Offset


@dataclass
class Page:
    """
    A page of search results from S3 with pagination support.

    Example:
    >>> page = bucket.search(prefix="data/", limit=10)
    >>> for key in page:
    ...     data = bucket.load(key)
    >>> if page.continues:
    ...     next_page = bucket.search(prefix="data/", next_token=page.next_token)
    """

    keys: list[str] = field(default_factory=list)
    next_token: Offset | None = None

    @property
    def continues(self) -> bool:
        return bool(self.next_token)

    def __len__(self) -> int:
        return len(self.keys)

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys)
