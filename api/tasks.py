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

from attributes import Attempt
from attributes import Email
from attributes import Identifier
from controllers import Controller
from controllers import ControllerRequest
from controllers import ControllerResponse
from enums import Action
from enums import Status
from exceptions import CoordinatorStepRequiresChildrenError
from exceptions import JobChildrenError
from exceptions import MaxTaskContinuationAttemptsError
from exceptions import MonitorStepRequiresChildrenError
from exceptions import ParallelStepRequiresParentError
from exceptions import RecordNotFoundError
from exceptions import SequenceStepJobNotInSiblingsError
from exceptions import SequenceStepRequiresParentError
from exceptions import StepContinuationError
from logger import get_logger
from messages import Message
from messages import Queue
from models import Job
from models import JobState
from models import User
from repositories import JobsRepository
from repositories import JobStateRepository
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
    """Report task response: status, job_id; optional job when found."""

    job: dict[str, Any]


class Task(Controller):
    """
    Base task: validate, execute, handler. Used by the worker for "run" and "report" actions.
    validate() is always called with a dict (body or {}), so subclasses can assume body is dict.
    Handler loads state via resume(), runs execute(), then save() and broadcast().

    For example, to run the start task:
    >>> task = StartTask()
    >>> result = task.handler({"job_id": "j1", "user_email": "u@e.com"})
    >>> result["status"]
    <Status.SUCCESS: 'success'>
    """

    def __init__(self):
        self.job: Job
        self.user: User
        self.state: dict[str, Any]
        self.attempt: Attempt

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

    @abstractmethod
    def broadcast(self) -> None:
        """Enqueue follow-up messages (e.g. START next, REPORT parent). Overridden by StartTask and ReportTask."""
        pass

    def handler(self, body: dict[str, Any] | None = None) -> TaskResponse:
        """
        Validate, load job and state (resume); if failed or max attempts, return; else execute, save, broadcast.
        """
        payload: dict[str, Any] = body if body is not None else {}
        validated: TaskRequest = self.validate(payload)
        self.user = User(email=validated["user_email"])
        try:
            self.job = self.repository.get(validated["job_id"])
        except RecordNotFoundError:
            return {"status": Status.FAILED}

        # If the job is already failed, log and return.
        if self.job.is_failed():
            logger.info("Task skipped: job already failed job_id=%s", self.job.id)
            return {"status": Status.FAILED, "job_id": self.job.id}

        # Load step state and attempt from JobStateRepository; may raise MaxTaskContinuationAttemptsError.
        try:
            self.resume()
        except MaxTaskContinuationAttemptsError:
            self.job.fail(MaxTaskContinuationAttemptsError("Max task continuation attempts reached"))
            self.save()
            logger.info("Task stopped: max continuation attempts job_id=%s", self.job.id)
            return {"status": Status.FAILED, "job_id": self.job.id}

        # The job is pending and within attempt limit. Run the execute method.
        try:
            result: TaskResponse = self.execute(validated)
        except StepContinuationError as err:
            # Step asked to continue in another Lambda: persist its state and re-queue START; do not save job or broadcast.
            self.state = dict(err.state)
            self.requeue()
            logger.debug("Task continuation: saved state and re-queued job_id=%s", self.job.id)
            return {"status": Status.PENDING, "job_id": self.job.id}

        # Execute completed normally: persist job and state, then broadcast (e.g. START next or REPORT parent).
        self.save()
        self.broadcast()
        return result

    def resume(self) -> None:
        """
        Load step state and attempt from JobStateRepository; set self.state and self.attempt.
        Raises MaxTaskContinuationAttemptsError if attempt > MAX_TASK_CONTINUATION_STEPS.

        If no state exists for this job, self.state = {} and self.attempt = Attempt(0).
        """
        try:
            job_state: JobState = self.state_repository.get(self.job.id)
            self.state = dict(job_state.data)
            self.attempt = Attempt(job_state.attempt)
        except RecordNotFoundError:
            self.state = {}
            self.attempt = Attempt(0)

    def save(self) -> None:
        """
        Persist job to repository and persist step state (flush) so state and job stay in sync.
        Called after execute() completes successfully; also when max continuation attempts is reached.
        """
        self.repository.save(self.job)
        self.flush()

    def flush(self) -> None:
        """
        Persist current step state to JobStateRepository. save() calls this to keep state durable.
        Does not increment attempt or enqueue messages.
        """
        job_state = JobState(id=self.job.id, data=dict(self.state), attempt=int(self.attempt))
        self.state_repository.save(job_state)

    def requeue(self) -> None:
        """
        Persist step state with incremented attempt and enqueue START for this job so the next run continues.
        Used only when StepContinuationError is caught; the next handler invocation will resume() and load this state.
        """
        job_state = JobState(id=self.job.id, data=dict(self.state), attempt=int(self.attempt) + 1)
        self.state_repository.save(job_state)
        message = Message(action=Action.START, job_id=self.job.id, user_email=self.user.email)
        queue.put(message)

    @cached_property
    def repository(self) -> JobsRepository:
        """JobsRepository for the task's user. Requires self.user set by handler."""
        return JobsRepository(user=self.user)

    @cached_property
    def state_repository(self) -> JobStateRepository:
        """JobStateRepository for the task's user. Requires self.user set by handler."""
        return JobStateRepository(user=self.user)

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
            step: Step = Step.of(self.job.step_name)(job=self.job, user=self.user, state=dict(self.state))
            stdout: dict[str, Any] = step.run(**meta)
            self.job = step.job
            self.job.stdout.update(stdout)
        except StepContinuationError as err:
            self.state = dict(err.state)
            raise
        except Exception as error:
            self.job.fail(error)
            logger.exception("StartTask.execute() | step failed job_id=%s step_name=%s error=%s", self.job.id, self.job.step_name, error)

        # Handler will call save() and broadcast(); we just return status and job_id.
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
        Enqueue START messages for the next work items based on step type; then enqueue REPORT for this job.
        Called after repository.save() in handler; does not enqueue REPORT until after step-type logic (caller calls self.report() at end).

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
        step: Step = Step.of(self.job.step_name)(job=self.job, user=self.user, state=dict(self.state))

        # CoordinatorStep: START the first child.
        if isinstance(step, CoordinatorStep):
            if not self.job.children_ids:
                raise CoordinatorStepRequiresChildrenError("CoordinatorStep requires children")
            self.start(self.job.children_ids[0])

        # SequenceStep: START next sibling (if any); REPORT parent is done by self.report() via ReportTask.
        if isinstance(step, SequenceStep):
            if self.job.parent_id is None:
                raise SequenceStepRequiresParentError("SequenceStep requires parent")
            try:
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
        self.report()


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

    def execute(self, validated_input: TaskRequest) -> ReportTaskResponse:
        logger.debug("ReportTask.execute() | aggregating job_id=%s children=%d", self.job.id, len(self.children))

        # Merge children stdout and meta into job.stdout and job.meta.
        for child in self.children:
            self.job.stdout.update(child.stdout)
            self.job.meta.update(child.meta)

        # If any child failed, merge children stderr into job.stderr and set job.status to FAILED.
        if any(child.is_failed() for child in self.children):
            for child in self.children:
                self.job.stderr.update(child.stderr)
            self.job.fail(JobChildrenError("One or more child jobs failed"))
            logger.info("ReportTask.execute() | job failed job_id=%s status=FAILED", self.job.id)

        elif any(child.is_pending() for child in self.children):
            # If any child is pending, leave job.status unchanged.
            # This same function will be called again when the child completes.
            pass

        else:

            # All children are successful, so set job.status to SUCCESS and finish the job.
            self.job.finish()
            logger.info("ReportTask.execute() | job completed job_id=%s status=SUCCESS", self.job.id)

        return {"status": self.job.status, "job_id": self.job.id, "job": self.job.serialize()}

    def broadcast(self) -> None:
        """
        Put a REPORT message for the parent; no-op if parent_id is None or job is pending.

        For example, to broadcast to parent job of completion (handler calls this after execute):
        >>> task = ReportTask()
        >>> task.job = some_job
        >>> task.user = some_user
        >>> task.broadcast()
        """
        if self.job.parent_id is None or self.job.is_pending():
            return
        message: Message = Message(action=Action.REPORT, job_id=self.job.parent_id, user_email=self.user.email)
        queue.put(message)
