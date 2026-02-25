"""
ReportTask: load job and its children; set job status from children (success/failed), save, enqueue REPORT for parent when present. Errors handled here.
"""

from __future__ import annotations

import logging
from typing import Any

from attributes import Email
from attributes import Identifier
from enums import Action
from enums import Status
from messages import Message
from messages import Queue
from models import Job
from models import User
from repositories.jobs import JobsRepository

from tasks.base import Task
from tasks.request import TaskRequest
from tasks.response import TaskResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

queue: Queue = Queue()


class ReportTaskResponse(TaskResponse, total=False):
    """Report task response: status, job_id; optional reason when failed; optional job when found."""

    reason: str
    job: dict[str, Any]


class ReportTask(Task[TaskRequest, ReportTaskResponse]):
    """
    Load job by id. If job is failed, return failed with reason.
    If job has no children: set job to SUCCESS, save; if parent_id put REPORT for parent.
    If job has children: load all (repository.get, no try/except). If any child is PENDING: return early.
    If any child is FAILED: set job to FAILED, save; if parent_id put REPORT for parent.
    If all children SUCCESS: set job to SUCCESS, merge children stdout into job, save; if parent_id put REPORT for parent.
    """

    def validate(self, body: dict[str, Any]) -> TaskRequest:
        return TaskRequest(
            job_id=Identifier(body.get("job_id")),
            user_email=Email(body.get("user_email")),
        )

    def execute(self, validated_input: TaskRequest) -> ReportTaskResponse:
        job_id: Identifier = validated_input["job_id"]
        user_email: Email = validated_input["user_email"]
        user: User = User(id=str(user_email), email=user_email)
        repository: JobsRepository = JobsRepository(user=user)
        job: Job = repository.get(job_id)
        if job.is_failed():
            return {
                "status": Status.FAILED,
                "job_id": job_id,
                "reason": "job_failed",
            }

        if not job.children_ids:
            job.status = Status.SUCCESS
            repository.save(job)
            logger.info("ReportTask: job %s (no children) set success", job_id)
            if job.parent_id is not None:
                queue.put(
                    Message(action=Action.REPORT, job_id=job.parent_id, user_email=user_email)
                )
            return {"status": Status.SUCCESS, "job_id": job_id, "job": job.serialize()}

        children: list[Job] = [repository.get(child_id) for child_id in job.children_ids]

        any_pending = any(c.is_pending() for c in children)
        if any_pending:
            return {"status": Status.SUCCESS, "job_id": job_id, "job": job.serialize()}

        any_failed = any(c.is_failed() for c in children)
        if any_failed:
            job.status = Status.FAILED
            repository.save(job)
            logger.info("ReportTask: job %s set failed (child failed)", job_id)
            if job.parent_id is not None:
                queue.put(
                    Message(action=Action.REPORT, job_id=job.parent_id, user_email=user_email)
                )
            return {"status": Status.SUCCESS, "job_id": job_id}

        job.status = Status.SUCCESS
        for child in children:
            job.stdout[str(child.id)] = dict(child.stdout)
        repository.save(job)
        logger.info("ReportTask: job %s set success, merged %d children stdout", job_id, len(children))
        if job.parent_id is not None:
            queue.put(
                Message(action=Action.REPORT, job_id=job.parent_id, user_email=user_email)
            )
        return {"status": Status.SUCCESS, "job_id": job_id, "job": job.serialize()}
