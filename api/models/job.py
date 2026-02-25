"""
Job model: async job with stdin/stdout, status, stage; used by the queue worker.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from attributes import Identifier
from attributes import Timestamp
from enums import Stage
from enums import Status

from models.base import Model


@dataclass
class Job(Model):
    """
    Job for async processing. parent_id, children_ids, status, stage, stdin, stdout, meta, stderr.

    Example:
    >>> job = Job(id=Identifier("abc"))
    >>> data = job.serialize()
    >>> job = Job.unserialize(data)
    """

    id: Identifier
    parent_id: Identifier | None = None
    children_ids: list[Identifier] = field(default_factory=list)
    status: Status = Status.PENDING
    stage: Stage = Stage.ART_GALLERY
    stdin: dict[str, Any] = field(default_factory=dict)
    stdout: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    stderr: dict[str, Any] = field(default_factory=dict)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)

    def __str__(self) -> str:
        return f"Job(id={self.id}, status={self.status}, stage={self.stage})"

    def __repr__(self) -> str:
        return f"Job(id={self.id!r}, status={self.status!r}, stage={self.stage!r})"

    def is_pending(self) -> bool:
        """Return True if job status is PENDING."""
        return self.status == Status.PENDING

    def is_failed(self) -> bool:
        """Return True if job status is FAILED."""
        return self.status == Status.FAILED

    def is_finished(self) -> bool:
        """Return True if job status is SUCCESS."""
        return self.status == Status.SUCCESS

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> Job:
        raw_children = data.get("children_ids") or []
        children_ids: list[Identifier] = [Identifier(c) if not isinstance(c, Identifier) else c for c in raw_children]
        parent_raw = data.get("parent_id")
        parent_id: Identifier | None = Identifier(parent_raw) if parent_raw else None
        status_raw = data.get("status")
        status: Status = Status.parse(status_raw) if status_raw else Status.PENDING
        stage_raw = data.get("stage") or data.get("task")
        stage: Stage = Stage.parse(stage_raw) if stage_raw else Stage.ART_GALLERY
        return cls(
            id=Identifier(data.get("id", "")),
            parent_id=parent_id,
            children_ids=children_ids,
            status=status,
            stage=stage,
            stdin=dict(data.get("stdin") or {}),
            stdout=dict(data.get("stdout") or {}),
            meta=dict(data.get("meta") or {}),
            stderr=dict(data.get("stderr") or {}),
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
        )

    def serialize(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "parent_id": str(self.parent_id) if self.parent_id is not None else None,
            "children_ids": [str(c) for c in self.children_ids],
            "status": self.status.value,
            "stage": self.stage.value,
            "stdin": dict(self.stdin),
            "stdout": dict(self.stdout),
            "meta": dict(self.meta),
            "stderr": dict(self.stderr),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }
