"""
Action-to-task mapping for the worker. Used by handler to dispatch by action.
"""

from __future__ import annotations

from typing import Type

from attributes import Action
from tasks import ReportTask
from tasks import RunTask
from tasks.base import Task

TASK_BY_ACTION: dict[str, Type[Task]] = {
    Action.RUN: RunTask,
    Action.REPORT: ReportTask,
}
