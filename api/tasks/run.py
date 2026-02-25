"""
RunTask: log job stdin, enqueue report message.
"""

from __future__ import annotations

import logging
from typing import Any

from exceptions import RecordNotFoundError
from exceptions import ValidationError
from messages import Message
from messages import Queue
from models import User
from repositories.jobs import JobsRepository
from attributes import Action

from tasks.base import RunTaskInput
from tasks.base import Task

logger = logging.getLogger()
logger.setLevel(logging.INFO)

queue = Queue()


class RunTask(Task[RunTaskInput]):
    """
    Log job stdin with logger.info and enqueue a "report" message.
    Returns early with status dict if job not found.

    Example:
    >>> task = RunTask()
    >>> result = task.handle(body={"job_id": "abc", "user_email": "u@e.com"})
    """

    def validate(self, body: dict[str, Any] | None = None) -> RunTaskInput:
        payload = body or {}
        job_id = payload.get("job_id")
        user_email = payload.get("user_email")
        if not job_id or not isinstance(job_id, str):
            raise ValidationError("job_id is required and must be a non-empty string")
        if not user_email or not isinstance(user_email, str):
            raise ValidationError("user_email is required and must be a non-empty string")
        return RunTaskInput(job_id=job_id, user_email=user_email)

    def execute(self, validated_input: RunTaskInput) -> dict[str, Any]:
        job_id = validated_input["job_id"]
        user_email = validated_input["user_email"]
        user = User(id=user_email, email=user_email)
        repo = JobsRepository(user=user)
        try:
            job = repo.get(job_id)
        except RecordNotFoundError:
            logger.info("RunTask: job not found, id=%s", job_id)
            return {"status": "skipped", "reason": "job_not_found", "job_id": job_id}
        logger.info("RunTask: job stdin=%s", job.stdin)
        queue.put(
            Message(
                action=Action(Action.REPORT),
                job_id=job_id,
                user_email=user_email,
            )
        )
        return {"status": "ok", "job_id": job_id}
