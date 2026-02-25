"""
ReportTask: load job and its children; set job status from children (success/failed), save, notify parent when done.
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
from tasks.response import ReportTaskResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)

queue: Queue = Queue()


class ReportTask(Task[TaskRequest, ReportTaskResponse]):
    """
    Load job by id. If job is failed, notify parent and return.
    Load all children (no try/except). Merge children stdout into job.stdout (dict update; keys override).
    If any child failed: merge children stderr into job.stderr, job.status = FAILED.
    If any child pending: leave status unchanged.
    Else: job.status = SUCCESS.
    Save job; if job is not pending, notify parent.
    """

    def notify(self, job: Job, user_email: Email) -> None:
        """Put a REPORT message for the parent; no-op if parent_id is None."""
        if job.parent_id is None:
            return
        message: Message = Message(action=Action.REPORT, job_id=job.parent_id, user_email=user_email)
        queue.put(message)

    def validate(self, body: dict[str, Any]) -> TaskRequest:
        return TaskRequest(
            job_id=Identifier(body.get("job_id")),
            user_email=Email(body.get("user_email")),
        )

    def execute(self, validated_input: TaskRequest) -> ReportTaskResponse:
        job_id: Identifier = validated_input["job_id"]
        user_email: Email = validated_input["user_email"]
        user: User = User(email=user_email)
        repository: JobsRepository = JobsRepository(user=user)
        job: Job = repository.get(job_id)

        if job.is_failed():
            self.notify(job, user_email)
            return {"status": Status.FAILED, "job_id": job_id, "reason": "job_failed"}

        children: list[Job] = [repository.get(cid) for cid in job.children_ids]
        for child in children:
            job.stdout.update(dict(child.stdout))

        if any(child.is_failed() for child in children):
            for child in children:
                job.stderr.update(dict(child.stderr))
            job.status = Status.FAILED
        elif any(child.is_pending() for child in children):
            pass
        else:
            job.status = Status.SUCCESS

        repository.save(job)
        if not job.is_pending():
            self.notify(job, user_email)

        return {"status": Status.SUCCESS, "job_id": job_id, "job": job.serialize()}
