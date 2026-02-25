"""
StartTask: log job stdin, enqueue report message. Returns failed with reason if job is failed.
"""

from __future__ import annotations

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
from tasks.response import StartTaskResponse

from api.logger import get_logger

logger = get_logger(__name__)

queue: Queue = Queue()


class StartTask(Task[TaskRequest, StartTaskResponse]):
    """
    Log job stdin with logger.info and enqueue a "report" message.
    Returns failed with reason if job is failed; does not enqueue further work.

    Example:
    >>> task = StartTask()
    >>> result = task.handle(body={"job_id": "abc", "user_email": "u@e.com"})
    """

    def validate(self, body: dict[str, Any]) -> TaskRequest:
        return TaskRequest(
            job_id=Identifier(body.get("job_id")),
            user_email=Email(body.get("user_email")),
        )

    def execute(self, validated_input: TaskRequest) -> StartTaskResponse:
        job_id: Identifier = validated_input["job_id"]
        user_email: Email = validated_input["user_email"]
        user: User = User(email=user_email)
        repository: JobsRepository = JobsRepository(user=user)
        job: Job = repository.get(job_id)
        if job.is_failed():
            return {
                "status": Status.FAILED,
                "job_id": job_id,
                "reason": "job_failed",
            }
        logger.info("StartTask.execute() | job stdin=%s", job.stdin)
        message: Message = Message(
            action=Action.REPORT,
            job_id=job.id,
            user_email=user_email,
        )
        queue.put(message)
        return {"status": Status.SUCCESS, "job_id": job_id}
