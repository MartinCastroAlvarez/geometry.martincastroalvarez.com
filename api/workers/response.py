"""
Worker response: handler return value (results list of TaskResponse).
"""

from __future__ import annotations

from typing import Any

from attributes import Identifier
from enums import Status
from interfaces import Serializable
from tasks.response import TaskResponse


class WorkerResponse(Serializable[dict[str, Any]]):
    """Handler return value: results list of TaskResponse."""

    def __init__(self, results: list[TaskResponse]) -> None:
        self.results: list[TaskResponse] = results

    def serialize(self) -> dict[str, Any]:
        serialized: list[dict[str, Any]] = []
        for item in self.results:
            out: dict[str, Any] = {}
            for key, value in item.items():
                if value is None:
                    out[key] = None
                elif isinstance(value, Status):
                    out[key] = value.value
                elif isinstance(value, Identifier):
                    out[key] = str(value)
                else:
                    out[key] = value
            serialized.append(out)
        return {"results": serialized}

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> WorkerResponse:
        raise NotImplementedError("WorkerResponse.unserialize is not used")
