"""
Base task interface: validate, execute, handle.

Title
-----
Task Base Class

Context
-------
Task is the abstract base for worker tasks. It is generic over request
(T) and response (R). validate(body) returns validated input T;
execute(validated_input) returns response R; handle(body) runs validate
then execute (body default {}). The worker passes the message body dict
to handle; validate can assume body is a dict. Used by StartTask and
ReportTask; dispatch is by Action via TASK_BY_ACTION in workers.urls.

Examples:
>>> class StartTask(Task[TaskRequest, StartTaskResponse]):
>>> def validate(self, body): ...
>>> def execute(self, validated_input): ...
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from tasks.request import TaskRequest
from tasks.response import TaskResponse

T = TypeVar("T", bound=TaskRequest)
R = TypeVar("R", bound=TaskResponse)


class Task(ABC, Generic[T, R]):
    """
    Base task: validate, execute, handle. Used by the worker for "run" and "report" actions.
    validate() is always called with a dict (body or {}), so subclasses can assume body is dict.
    """

    @abstractmethod
    def validate(self, body: dict[str, Any]) -> T:
        raise NotImplementedError

    @abstractmethod
    def execute(self, validated_input: T) -> R:
        raise NotImplementedError

    def handle(self, body: dict[str, Any] | None = None) -> R:
        payload: dict[str, Any] = body if body is not None else {}
        validated_input = self.validate(payload)
        return self.execute(validated_input)
