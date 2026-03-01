"""
Background tasks invoked by the worker Lambda.

Title
-----
Tasks Module

Context
-------
This module defines the worker tasks: StartTask and ReportTask. Task is
the base (validate, execute, handler). StartTask maps job.step_name to
a Step (api/steps.py), runs step.run(**meta), updates job from step.job
and merges run output into job.stdout, saves the job, and enqueues REPORT
unless the step is ArtGalleryStep (which enqueues REPORT itself). Returns
FAILED if job already failed. ReportTask loads job and children, merges
children stdout/stderr into job, sets status (SUCCESS/FAILED), saves, and
notifies parent with REPORT. TaskRequest has job_id, user_email, and
optional meta; TaskResponse has status and optional job_id, error, traceback.
Used by workers.handler and workers (ROUTES).

Examples:
>>> task = StartTask()
>>> result = task.handler(body={"job_id": "abc", "user_email": "u@e.com"})
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from typing import NotRequired

from attributes import Email
from attributes import Identifier
from controllers import Controller
from controllers import ControllerRequest
from controllers import ControllerResponse
from enums import Action
from enums import Status
from enums import StepName
from logger import get_logger
from messages import Message
from messages import Queue
from models import Job
from models import User
from repositories import JobsRepository
from steps import STEP_CLASS_BY_NAME
from steps import ArtGalleryStep
from steps import Step

logger = get_logger(__name__)

queue: Queue = Queue()


class TaskRequest(ControllerRequest):
    """Task request: job_id, user_email, and optional meta for step run()."""

    job_id: Identifier
    user_email: Email
    meta: NotRequired[dict[str, Any]]


class TaskResponse(ControllerResponse):
    """Base task response: status (required); optional job_id, error, traceback."""

    status: Status
    job_id: NotRequired[Identifier]
    error: NotRequired[str]
    traceback: NotRequired[list[str]]


class StartTaskResponse(TaskResponse):
    """Start task response: status, job_id; optional reason when job failed."""

    reason: str


class ReportTaskResponse(TaskResponse):
    """Report task response: status, job_id; optional reason when failed; optional job when found."""

    reason: str
    job: dict[str, Any]


class Task(Controller):
    """
    Base task: validate, execute, handler. Used by the worker for "run" and "report" actions.
    validate() is always called with a dict (body or {}), so subclasses can assume body is dict.

    For example, to run the start task:
    >>> task = StartTask()
    >>> result = task.handler({"job_id": "j1", "user_email": "u@e.com"})
    >>> result["status"]
    <Status.SUCCESS: 'success'>
    """

    @abstractmethod
    def validate(self, body: dict[str, Any]) -> TaskRequest:
        pass

    @abstractmethod
    def execute(self, validated_input: TaskRequest) -> TaskResponse:
        pass

    def handler(self, body: dict[str, Any] | None = None) -> TaskResponse:
        """Override to default body to {} when None (worker passes body or empty)."""
        payload: dict[str, Any] = body if body is not None else {}
        return super().handler(payload)


class StartTask(Task):
    """
    Log job stdin with logger.info and enqueue a "report" message.
    Returns failed with reason if job is failed; does not enqueue further work.

    For example, to start processing a job:
    >>> task = StartTask()
    >>> result = task.handler({"job_id": "j1", "user_email": "u@e.com"})
    >>> result["status"] == Status.SUCCESS
    True
    """

    def validate(self, body: dict[str, Any]) -> TaskRequest:
        req: TaskRequest = {
            "job_id": Identifier(body.get("job_id")),
            "user_email": Email(body.get("user_email")),
        }
        meta = body.get("meta")
        if meta is not None and isinstance(meta, dict):
            req["meta"] = meta
        return req

    def execute(self, validated_input: TaskRequest) -> StartTaskResponse:
        job_id: Identifier = validated_input["job_id"]
        user_email: Email = validated_input["user_email"]
        meta: dict[str, Any] = validated_input.get("meta") or {}
        user: User = User(email=user_email)
        repository: JobsRepository = JobsRepository(user=user)
        job: Job = repository.get(job_id)
        if job.is_failed():
            return {
                "status": Status.FAILED,
                "job_id": job_id,
                "reason": "job_failed",
            }
        step_name: StepName = job.step_name
        step_class = STEP_CLASS_BY_NAME.get(step_name)
        if step_class is None:
            logger.warning("StartTask.execute() | unknown step_name=%s job_id=%s", step_name, job_id)
            return {"status": Status.FAILED, "job_id": job_id, "reason": "unknown_step"}
        step: Step = step_class(job=job, user_email=user_email)
        run_output: dict[str, Any] = step.run(**meta)
        job = step.job
        job.stdout.update(run_output)
        repository.save(job)
        if not isinstance(step, ArtGalleryStep):
            message: Message = Message(
                action=Action.REPORT,
                job_id=job.id,
                user_email=user_email,
                meta=meta if meta else None,
            )
            queue.put(message)
        return {"status": Status.SUCCESS, "job_id": job_id}


class ReportTask(Task):
    """
    Load job by id. If job is failed, notify parent and return.
    Load all children (no try/except). Merge children stdout into job.stdout (dict update; keys override).
    If any child failed: merge children stderr into job.stderr, job.status = FAILED.
    If any child pending: leave status unchanged.
    Else: job.status = SUCCESS.
    Save job; if job is not pending, notify parent.

    For example, to run the report task (aggregate children):
    >>> task = ReportTask()
    >>> result = task.handler({"job_id": "j1", "user_email": "u@e.com"})
    >>> "job" in result
    True
    """

    def notify(self, job: Job, user_email: Email) -> None:
        """
        Put a REPORT message for the parent; no-op if parent_id is None.

        For example, to notify parent job of completion:
        >>> task.notify(job, user_email)
        """
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
            logger.info("ReportTask.execute() | job already failed job_id=%s", job_id)
            self.notify(job, user_email)
            return {"status": Status.FAILED, "job_id": job_id, "reason": "job_failed"}

        children: list[Job] = [repository.get(cid) for cid in job.children_ids]
        logger.debug("ReportTask.execute() | aggregating job_id=%s children=%d", job_id, len(children))
        for child in children:
            job.stdout.update(dict(child.stdout))

        if any(child.is_failed() for child in children):
            for child in children:
                job.stderr.update(dict(child.stderr))
            job.status = Status.FAILED
            logger.info("ReportTask.execute() | job failed job_id=%s status=FAILED", job_id)
        elif any(child.is_pending() for child in children):
            pass
        else:
            job.status = Status.SUCCESS
            logger.info("ReportTask.execute() | job completed job_id=%s status=SUCCESS", job_id)

        repository.save(job)
        if not job.is_pending():
            self.notify(job, user_email)

        return {"status": Status.SUCCESS, "job_id": job_id, "job": job.serialize()}
