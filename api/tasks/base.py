"""
Base task interface: validate, execute, handle.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Generic
from typing import TypeVar

from tasks.request import TaskRequest
from tasks.response import TaskResponse

I = TypeVar("I", bound=TaskRequest)
O = TypeVar("O", bound=TaskResponse)


class Task(ABC, Generic[I, O]):
    """
    Base task: validate, execute, handle. Used by the worker for "run" and "report" actions.
    validate() is always called with a dict (body or {}), so subclasses can assume body is dict.
    """

    @abstractmethod
    def validate(self, body: dict[str, Any]) -> I:
        raise NotImplementedError

    @abstractmethod
    def execute(self, validated_input: I) -> O:
        raise NotImplementedError

    def handle(self, body: dict[str, Any] | None = None) -> O:
        payload: dict[str, Any] = body if body is not None else {}
        validated_input = self.validate(payload)
        return self.execute(validated_input)
