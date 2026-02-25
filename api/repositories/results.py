"""
Paginated results from repository search.
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
