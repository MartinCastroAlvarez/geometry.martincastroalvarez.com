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

T = TypeVar("T")


@dataclass
class Results(Generic[T]):
    """
    Paginated results from a repository search.

    Example:
    >>> results = repo.search(next_token=token, limit=20)
    >>> for record in results:
    ...     process(record)
    >>> return {"records": [r.to_dict() for r in results.records], "next_token": results.next_token}
    """

    records: list[T] = field(default_factory=list)
    next_token: str = field(default="")

    def __iter__(self) -> Iterator[T]:
        return iter(self.records)

    def __len__(self) -> int:
        return len(self.records)

    def to_dict(self) -> dict[str, Any]:
        return {
            "records": [r.to_dict() for r in self.records],
            "next_token": self.next_token,
        }
