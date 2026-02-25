"""
Job model: async job with stdin/stdout, status, task; used by the queue worker.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from attributes import Identifier
from attributes import Timestamp

from models.base import Model


@dataclass
class Job(Model):
    """
    Job for async processing. parent_id, children_ids, status, task, stdin, stdout, meta, stderr.

    Example:
    >>> job = Job(id="abc", parent_id="", children_ids=[], status="pending", task="art_gallery", stdin={}, stdout={}, meta={}, stderr={})
    >>> data = job.to_dict()
    >>> job = Job.from_dict(data)
    """

    id: Identifier
    parent_id: str
    children_ids: list[str]
    status: str
    task: str
    stdin: dict[str, Any]
    stdout: dict[str, Any]
    meta: dict[str, str]
    stderr: dict[str, Any]
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)

    def __str__(self) -> str:
        return f"Job(id={self.id}, status={self.status}, task={self.task})"

    def __repr__(self) -> str:
        return f"Job(id={self.id!r}, status={self.status!r}, task={self.task!r})"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Job:
        return cls(
            id=Identifier(str(data.get("id", ""))),
            parent_id=str(data.get("parent_id", "")),
            children_ids=list(data.get("children_ids") or []),
            status=str(data.get("status", "")),
            task=str(data.get("task", "")),
            stdin=dict(data.get("stdin") or {}),
            stdout=dict(data.get("stdout") or {}),
            meta=dict(data.get("meta") or {}),
            stderr=dict(data.get("stderr") or {}),
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "parent_id": self.parent_id,
            "children_ids": list(self.children_ids),
            "status": self.status,
            "task": self.task,
            "stdin": dict(self.stdin),
            "stdout": dict(self.stdout),
            "meta": dict(self.meta),
            "stderr": dict(self.stderr),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
