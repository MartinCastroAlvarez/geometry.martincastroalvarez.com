"""
Action-to-task mapping for the worker. Used by handler to dispatch by action.
"""

from __future__ import annotations

from typing import Any
from typing import Type

from enums import Action
from tasks import ReportTask
from tasks import StartTask
from tasks.base import Task

TASK_BY_ACTION: dict[Action, Type[Task[Any, Any]]] = {
    Action.START: StartTask,
    Action.REPORT: ReportTask,
}
