"""
Paginated results from repository search.

Title
-----
Results (Paginated Repository Search)

Context
-------
Results holds one page of repository search: records (list of model
instances) and next_token (Offset | None). Iterable over records; len()
returns record count. serialize() returns dict with records (each
serialized) and next_token string for API response. Used by
Repository.search and by query handlers that return list responses.

Examples:
    results = repo.search(next_token=token, limit=Limit(20))
    for record in results:
        process(record)
    return {"records": [r.serialize() for r in results.records], "next_token": results.next_token}
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Generic
from typing import Iterator
from typing import TypeVar

from attributes import Offset

T = TypeVar("T")


@dataclass
class Results(Generic[T]):
    """
    Paginated results from a repository search.

    Example:
    >>> results = repo.search(next_token=token, limit=Limit(20))
    >>> for record in results:
    ...     process(record)
    >>> return {"records": [r.serialize() for r in results.records], "next_token": results.next_token}
    """

    records: list[T] = field(default_factory=list)
    next_token: Offset | None = None

    def __iter__(self) -> Iterator[T]:
        return iter(self.records)

    def __len__(self) -> int:
        return len(self.records)

    def serialize(self) -> dict[str, Any]:
        return {
            "records": [r.serialize() for r in self.records],
            "next_token": str(self.next_token) if self.next_token else "",
        }
