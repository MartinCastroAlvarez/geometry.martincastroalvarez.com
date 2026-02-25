"""
Base task interface: validate, execute, handle.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar
from typing import TypedDict

T = TypeVar("T", bound="TaskInput")


class TaskInput(TypedDict):
    """Base for task inputs."""

    pass


class RunTaskInput(TaskInput):
    """Run task: job_id and user_email from message."""

    job_id: str
    user_email: str


class ReportTaskInput(TaskInput):
    """Report task: job_id and user_email from message."""

    job_id: str
    user_email: str


class Task(ABC, Generic[T]):
    """
    Base task: validate, execute, handle. Used by the worker for "run" and "report" actions.

    Example:
    >>> task = RunTask()
    >>> result = task.handle(body=message_body)
    """

    @abstractmethod
    def validate(self, body: dict[str, Any] | None = None) -> T:
        raise NotImplementedError

    @abstractmethod
    def execute(self, validated_input: T) -> dict[str, Any]:
        raise NotImplementedError

    def handle(self, body: dict[str, Any] | None = None) -> dict[str, Any]:
        validated_input = self.validate(body)
        return self.execute(validated_input)
