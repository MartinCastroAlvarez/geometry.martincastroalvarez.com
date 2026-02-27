"""
Action-to-task mapping for the worker. Used by handler to dispatch by action.

Title
-----
Worker Task Routing (TASK_BY_ACTION)

Context
-------
TASK_BY_ACTION maps each Action to the Task class that handles it:
Action.START -> StartTask, Action.REPORT -> ReportTask. The worker
handler looks up the task class from the message action, instantiates
it, and calls handle(body). Adding a new action requires a new Task
subclass and an entry here. Used only by workers.handler.

Examples:
>>> task_class = TASK_BY_ACTION.get(action)
>>> result = task_class().handle(body=body)
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
