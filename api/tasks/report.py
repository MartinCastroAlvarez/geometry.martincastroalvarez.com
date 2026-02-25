"""
ReportTask: load job and log it.
"""

from __future__ import annotations

import logging
from typing import Any

from exceptions import RecordNotFoundError
from exceptions import ValidationError
from models import User
from repositories.jobs import JobsRepository

from tasks.base import ReportTaskInput
from tasks.base import Task

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ReportTask(Task[ReportTaskInput]):
    """
    Load job by id and log it with logger.info.
    Returns early with status dict if job not found.

    Example:
    >>> task = ReportTask()
    >>> result = task.handle(body={"job_id": "abc", "user_email": "u@e.com"})
    """

    def validate(self, body: dict[str, Any] | None = None) -> ReportTaskInput:
        payload = body or {}
        job_id = payload.get("job_id")
        user_email = payload.get("user_email")
        if not job_id or not isinstance(job_id, str):
            raise ValidationError("job_id is required and must be a non-empty string")
        if not user_email or not isinstance(user_email, str):
            raise ValidationError("user_email is required and must be a non-empty string")
        return ReportTaskInput(job_id=job_id, user_email=user_email)

    def execute(self, validated_input: ReportTaskInput) -> dict[str, Any]:
        job_id = validated_input["job_id"]
        user_email = validated_input["user_email"]
        user = User(id=user_email, email=user_email)
        repo = JobsRepository(user=user)
        try:
            job = repo.get(job_id)
        except RecordNotFoundError:
            logger.info("ReportTask: job not found, id=%s", job_id)
            return {"status": "skipped", "reason": "job_not_found", "job_id": job_id}
        logger.info("ReportTask: job=%s", job)
        return {"status": "ok", "job_id": job_id, "job": job.to_dict()}
