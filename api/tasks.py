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
and merges run output into job.stdout, saves the job, and calls broadcast()
to enqueue REPORT for the job. Returns
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
from functools import cached_property
from typing import Any
from typing import NotRequired

from attributes import Email
from attributes import Identifier
from controllers import Controller
from controllers import ControllerRequest
from controllers import ControllerResponse
from enums import Action
from enums import Status
from exceptions import CoordinatorStepRequiresChildrenError
from exceptions import JobChildrenError
from exceptions import MonitorStepRequiresChildrenError
from exceptions import ParallelStepRequiresParentError
from exceptions import RecordNotFoundError
from exceptions import SequenceStepJobNotInSiblingsError
from exceptions import SequenceStepRequiresParentError
from logger import get_logger
from messages import Message
from messages import Queue
from models import Job
from models import User
from repositories import JobsRepository
from steps import CoordinatorStep
from steps import MonitorStep
from steps import ParallelStep
from steps import SequenceStep
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
    """Start task response: status, job_id."""

    reason: NotRequired[str]


class ReportTaskResponse(TaskResponse):
    """Report task response: status, job_id; optional reason when failed; optional job when found."""

    reason: str
    job: dict[str, Any]


class Task(Controller):
    """
    Base task: validate, execute, handler. Used by the worker for "run" and "report" actions.
    validate() is always called with a dict (body or {}), so subclasses can assume body is dict.
    Handler sets self.job from the repository after validation; execute() may use self.job, self.repository, self.parent.

    For example, to run the start task:
    >>> task = StartTask()
    >>> result = task.handler({"job_id": "j1", "user_email": "u@e.com"})
    >>> result["status"]
    <Status.SUCCESS: 'success'>
    """

    def __init__(self):
        self.job: Job
        self.user: User

    def validate(self, body: dict[str, Any]) -> TaskRequest:
        """Parse body into TaskRequest (job_id, user_email, optional meta)."""
        request: TaskRequest = {
            "job_id": Identifier(body.get("job_id")),
            "user_email": Email(body.get("user_email")),
        }
        meta: Any = body.get("meta")
        if meta is not None and isinstance(meta, dict):
            request["meta"] = meta
        return request

    @abstractmethod
    def execute(self, validated_input: TaskRequest) -> TaskResponse:
        pass

    def handler(self, body: dict[str, Any] | None = None) -> TaskResponse:
        """Validate, load job into self.job; if job is failed log and return, else run execute."""
        payload: dict[str, Any] = body if body is not None else {}
        validated: TaskRequest = self.validate(payload)
        self.user: User = User(email=validated["user_email"])
        try:
            self.job: Job = self.repository.get(validated["job_id"])
        except RecordNotFoundError:
            return {"status": Status.FAILED}

        # If the job is already failed, log and return.
        if self.job.is_failed():
            logger.info("Task skipped: job already failed job_id=%s", self.job.id)
            return {"status": Status.FAILED, "job_id": self.job.id}

        # The job is pending, or not failed. Run the execute method.
        return self.execute(validated)

    @cached_property
    def repository(self) -> JobsRepository:
        """JobsRepository for the task's user. Requires self.user set by handler."""
        return JobsRepository(user=self.user)

    @cached_property
    def parent(self) -> Job | None:
        """Parent job from repository, or None if this job has no parent."""
        if self.job.parent_id is None:
            return None
        return self.repository.get(self.job.parent_id)

    @cached_property
    def siblings(self) -> list[Identifier]:
        """List of sibling job ids (parent's children_ids), or empty if no parent."""
        if self.parent is None:
            return []
        return list(self.parent.children_ids)

    @cached_property
    def children(self) -> list[Job]:
        """List of child jobs (loaded from repository by job.children_ids)."""
        return [self.repository.get(cid) for cid in self.job.children_ids]


class StartTask(Task):
    """
    Log job stdin with logger.info and enqueue a "report" message.
    Returns failed if job is failed; does not enqueue further work.

    For example, to start processing a job:
    >>> task = StartTask()
    >>> result = task.handler({"job_id": "j1", "user_email": "u@e.com"})
    >>> result["status"] == Status.SUCCESS
    True
    """

    def execute(self, validated_input: TaskRequest) -> StartTaskResponse:
        self.job.start()

        # If this job has a parent, inherit parent's stdout and all previous siblings' stdout
        # so the step has the full pipeline state (e.g. ear_clipping needs stitched from stitching).
        if self.job.parent_id is not None:
            parent_job: Job = self.parent
            self.job.stdout.update(parent_job.stdout)
            sibling_ids: list[Identifier] = list(parent_job.children_ids)
            try:
                my_idx: int = sibling_ids.index(self.job.id)
            except ValueError:
                my_idx = -1
            for prev_idx in range(my_idx):
                prev_job: Job = self.repository.get(sibling_ids[prev_idx])
                self.job.stdout.update(prev_job.stdout)

        # Execute the step, and capture any error.
        try:
            meta: dict[str, Any] = validated_input.get("meta") or {}
            step: Step = Step.of(self.job.step_name)(job=self.job, user=self.user)
            stdout: dict[str, Any] = step.run(**meta)
            self.job = step.job
            self.job.stdout.update(stdout)
        except Exception as error:
            self.job.fail(error)
            logger.exception("StartTask.execute() | step failed job_id=%s step_name=%s error=%s", self.job.id, self.job.step_name, error)

        # Save the job, start next children, and/or notify parent.
        self.repository.save(self.job)
        self.broadcast()
        self.report()
        return {"status": self.job.status, "job_id": self.job.id}

    def start(self, job_id: Identifier) -> None:
        """Put a message to START the given job_id."""
        logger.debug("StartTask.start() | job_id=%s", job_id)
        message: Message = Message(action=Action.START, job_id=job_id, user_email=self.user.email)
        queue.put(message)

    def report(self) -> None:
        """Put a message to REPORT self.job.id so ReportTask runs (aggregate or notify parent)."""
        logger.debug("StartTask.report() | job_id=%s", self.job.id)
        message: Message = Message(action=Action.REPORT, job_id=self.job.id, user_email=self.user.email)
        queue.put(message)

    def broadcast(self) -> None:
        """
        Enqueue START messages for the next work items based on step type.
        Called after repository.save() in execute(); does not enqueue REPORT (caller calls self.report() after).

        If self.job is failed, returns immediately without enqueuing anything.
        Otherwise builds the step via Step.of(self.job.step_name) to decide what to enqueue.

        Step-type behavior (a step may satisfy more than one; each branch runs independently):
        - CoordinatorStep: enqueue START for the first child (self.job.children_ids[0]). Raises if job has no children.
        - SequenceStep: require job has a parent; find this job's index in parent.children_ids. If not last,
          enqueue START for the next sibling. Parent notification is done by self.report() when ReportTask runs.
        - MonitorStep: enqueue START for every child in self.job.children_ids. Raises if job has no children.
        - ParallelStep: require job has a parent (no messages enqueued here; parent notification via self.report() and ReportTask).
        """
        if self.job.is_failed():
            return
        step: Step = Step.of(self.job.step_name)(job=self.job, user=self.user)

        # CoordinatorStep: START the first child.
        if isinstance(step, CoordinatorStep):
            if not self.job.children_ids:
                raise CoordinatorStepRequiresChildrenError("CoordinatorStep requires children")
            self.start(self.job.children_ids[0])

        # SequenceStep: START next sibling (if any); REPORT parent is done by self.report() via ReportTask.
        if isinstance(step, SequenceStep):
            try:
                if self.job.parent_id is None:
                    raise SequenceStepRequiresParentError("SequenceStep requires parent")
                parent_job: Job = self.repository.get(self.job.parent_id)
            except RecordNotFoundError:
                raise SequenceStepRequiresParentError("SequenceStep requires parent")
            sibling_ids: list[Identifier] = list(parent_job.children_ids)
            try:
                idx: int = sibling_ids.index(self.job.id)
            except ValueError:
                raise SequenceStepJobNotInSiblingsError("Job not in parent children_ids")
            if idx < len(sibling_ids) - 1:
                self.start(sibling_ids[idx + 1])

        # MonitorStep: START all children.
        if isinstance(step, MonitorStep):
            if not self.job.children_ids:
                raise MonitorStepRequiresChildrenError("MonitorStep requires children")
            for cid in self.job.children_ids:
                self.start(cid)

        # ParallelStep: require parent; REPORT parent is done by self.report() via ReportTask.
        if isinstance(step, ParallelStep):
            if self.job.parent_id is None:
                raise ParallelStepRequiresParentError("ParallelStep requires parent")
            pass


class ReportTask(Task):
    """
    Load job by id. If job is failed, broadcast to parent and return.
    Load all children (no try/except). Merge children stdout into job.stdout (dict update; keys override).
    If any child failed: merge children stderr into job.stderr, job.status = FAILED.
    If any child pending: leave status unchanged.
    Else: job.status = SUCCESS.
    Save job; if job is not pending, broadcast to parent.

    For example, to run the report task (aggregate children):
    >>> task = ReportTask()
    >>> result = task.handler({"job_id": "j1", "user_email": "u@e.com"})
    >>> "job" in result
    True
    """

    def broadcast(self, job: Job, user_email: Email) -> None:
        """
        Put a REPORT message for the parent; no-op if parent_id is None or job is pending.

        For example, to broadcast to parent job of completion:
        >>> task.broadcast(job, user_email)
        """
        if job.parent_id is None or job.is_pending():
            return
        message: Message = Message(action=Action.REPORT, job_id=job.parent_id, user_email=user_email)
        queue.put(message)

    def execute(self, validated_input: TaskRequest) -> ReportTaskResponse:
        logger.debug("ReportTask.execute() | aggregating job_id=%s children=%d", self.job.id, len(self.children))
        for child in self.children:
            self.job.stdout.update(child.stdout)
            self.job.meta.update(child.meta)
        if any(child.is_failed() for child in self.children):
            for child in self.children:
                self.job.stderr.update(child.stderr)
            self.job.fail(JobChildrenError("One or more child jobs failed"))
            logger.info("ReportTask.execute() | job failed job_id=%s status=FAILED", self.job.id)
        elif any(child.is_pending() for child in self.children):
            pass
        else:
            self.job.finish()
            logger.info("ReportTask.execute() | job completed job_id=%s status=SUCCESS", self.job.id)

        self.repository.save(self.job)
        self.broadcast(self.job, self.user.email)
        reason: str = "job_failed" if self.job.is_failed() else ""
        return {"status": self.job.status, "job_id": self.job.id, "job": self.job.serialize(), "reason": reason}
