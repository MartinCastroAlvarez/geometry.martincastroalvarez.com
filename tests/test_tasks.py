"""Tests for tasks package."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from attributes import Attempt
from attributes import Duration
from attributes import Email
from attributes import Identifier
from enums import Action
from enums import Status
from enums import StepName
from exceptions import EarClippingFailureError
from exceptions import MaxTaskContinuationAttemptsError
from exceptions import RecordNotFoundError
from exceptions import StepNotHandledError
from exceptions import SuspendedStepError
from models import Job
from models import JobState
from steps import Step
from tasks import ReportTask
from tasks import StartTask
from tasks import Task
from tasks import TaskResponse


class TestTaskResponse:
    """Test task response types."""

    def test_task_response_typed(self):
        r: TaskResponse = {"status": Status.SUCCESS}
        assert r["status"] == Status.SUCCESS


class TestTaskHandler:
    """Test Task.handler default body."""

    @patch.object(StartTask, "broadcast")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_handler_body_none_defaults_to_empty_dict(self, mock_repo_cls, mock_state_repo_cls, mock_broadcast):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        mock_job = MagicMock()
        mock_job.is_failed.return_value = False
        mock_job.id = Identifier("j1")
        mock_repo.get.return_value = mock_job
        with patch.object(StartTask, "validate", return_value={"job_id": Identifier("j1"), "user_email": Email("u@e.com")}) as mock_validate:
            with patch.object(StartTask, "execute", return_value={"status": Status.SUCCESS, "job_id": Identifier("j1")}) as mock_execute:
                task = StartTask()
                task.handler(body=None)
                mock_validate.assert_called_once_with({})
                mock_execute.assert_called_once()


class TestTaskFlushRequeue:
    """Test Task.flush() and Task.requeue() behavior."""

    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_flush_updates_job_meta_attempt(self, mock_repo_cls, mock_state_repo_cls):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo = MagicMock()
        mock_state_repo_cls.return_value = mock_state_repo
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.STITCHING,
            status=Status.PENDING,
            meta={},
        )
        task = StartTask()
        task.user = MagicMock()
        task.user.email = Email("u@e.com")
        task.job = job
        task.state = {"key": "value"}
        task.attempt = Attempt(0)
        task.flush()
        assert job.meta["step:stitching:attempt"] == 1
        call_args = mock_state_repo.save.call_args[0][0]
        assert call_args.attempt == 1
        assert call_args.data == {"key": "value"}

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_requeue_calls_save(self, mock_repo_cls, mock_state_repo_cls, mock_queue):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo = MagicMock()
        mock_state_repo_cls.return_value = mock_state_repo
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.STITCHING,
            status=Status.PENDING,
            meta={},
        )
        task = StartTask()
        task.user = MagicMock()
        task.user.email = Email("u@e.com")
        task.job = job
        task.state = {}
        task.attempt = Attempt(0)
        task.requeue()
        mock_repo.save.assert_called_once_with(job)
        assert mock_state_repo.save.call_count >= 1
        mock_queue.put.assert_called_once()


class TestStartTask:
    """Test StartTask validate and execute with mocks."""

    def test_validate_with_meta(self):
        task = StartTask()
        req = task.validate({"job_id": "j1", "user_email": "u@e.com", "meta": {"key": "v"}})
        assert req["job_id"] == Identifier("j1")
        assert req["meta"] == {"key": "v"}

    @patch("tasks.queue")
    @patch("tasks.JobsRepository")
    def test_execute_job_failed_returns_failed_no_queue_put(self, mock_repo_cls, mock_queue):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        job = MagicMock()
        job.is_failed.return_value = True
        job.id = Identifier("j1")
        mock_repo.get.return_value = job
        task = StartTask()
        req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
        result = task.handler(req)
        assert result["status"] == Status.FAILED
        mock_queue.put.assert_not_called()

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_execute_unknown_step_raises_step_not_handled(self, mock_repo_cls, mock_state_repo_cls, mock_queue):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.ART_GALLERY,
            status=Status.PENDING,
        )
        mock_repo.get.return_value = job
        with patch.object(Step, "of", side_effect=StepNotHandledError("Step cannot be handled: art_gallery")):
            task = StartTask()
            req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
            response = task.handler(req)
            assert response["status"] == Status.FAILED
            assert job.status == Status.FAILED
            assert "error:art-gallery:message" in job.stderr

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_execute_success_enqueues_report_for_non_art_gallery_step(
        self, mock_repo_cls, mock_state_repo_cls, mock_tasks_queue
    ):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        parent_id = Identifier("parent-1")
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.STITCHING,
            stdin={"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []},
            stdout={},
            children_ids=[],
            parent_id=parent_id,
        )
        parent_job = Job(
            id=parent_id,
            step_name=StepName.ART_GALLERY,
            stdin={},
            stdout={},
            children_ids=[job.id],
            parent_id=None,
        )
        mock_repo.get.side_effect = lambda id: parent_job if id == parent_id else job
        task = StartTask()
        req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
        result = task.handler(req)
        # Job stays PENDING until ReportTask runs; execute completed successfully; handler calls save() and broadcast() (report).
        assert result["status"] == Status.PENDING
        started_at_key = "step:stitching:started_at"
        assert started_at_key in job.meta
        assert isinstance(job.meta[started_at_key], str)
        assert "T" in job.meta[started_at_key]
        mock_tasks_queue.put.assert_called()
        mock_repo.save.assert_called_once()

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_execute_step_with_empty_stdout_returns_pending(
        self, mock_repo_cls, mock_state_repo_cls, mock_tasks_queue
    ):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        parent_id = Identifier("parent-1")
        # job.start() clears stdout before step runs, so StitchingStep gets an empty stdout
        # and runs successfully with 0 boundary points (no exception raised).
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.STITCHING,
            stdin={},
            stdout={"boundary": 123, "obstacles": []},
            children_ids=[],
            parent_id=parent_id,
        )
        parent_job = Job(
            id=parent_id,
            step_name=StepName.ART_GALLERY,
            stdin={},
            stdout={},
            children_ids=[job.id],
            parent_id=None,
        )
        mock_repo.get.side_effect = lambda id: parent_job if id == parent_id else job
        task = StartTask()
        req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
        result = task.handler(req)
        # stdout is cleared by job.start(), so no exception is raised; handler calls save() and broadcast().
        assert result["status"] == Status.PENDING
        mock_repo.save.assert_called_once()
        mock_tasks_queue.put.assert_called()

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    @patch("tasks.Step")
    def test_execute_step_raises_marks_job_failed_and_saves_stderr(
        self, mock_step_cls, mock_repo_cls, mock_state_repo_cls, mock_tasks_queue
    ):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.STITCHING,
            stdin={},
            stdout={},
            children_ids=[],
            parent_id=None,
        )
        mock_repo.get.return_value = job
        mock_step_instance = MagicMock()
        mock_step_instance.run.side_effect = ValueError("test error")
        mock_step_instance.job = job
        mock_step_cls.of.return_value.return_value = mock_step_instance
        task = StartTask()
        req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
        result = task.handler(req)
        assert result["status"] == Status.FAILED
        assert job.status == Status.FAILED
        assert "error:stitching" in str(job.stderr)
        mock_repo.save.assert_called_once()
        # When job is failed, broadcast() returns without enqueuing; no put expected.
        mock_tasks_queue.put.assert_not_called()

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    @patch("tasks.Step")
    def test_execute_ear_clipping_failure_saves_job_failed_with_error_in_stderr(
        self, mock_step_cls, mock_repo_cls, mock_state_repo_cls, mock_tasks_queue
    ):
        """When EarClippingStep raises EarClippingFailureError, job is saved as FAILED with error in stderr."""
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.EAR_CLIPPING,
            stdin={},
            stdout={"stitched": [[0, 0], [10, 0], [10, 10], [0, 10]]},
            children_ids=[],
            parent_id=None,
        )
        mock_repo.get.return_value = job
        mock_step_instance = MagicMock()
        mock_step_instance.run.side_effect = EarClippingFailureError("No valid ear found for polygon")
        mock_step_instance.job = job
        mock_step_cls.of.return_value.return_value = mock_step_instance
        task = StartTask()
        req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
        result = task.handler(req)
        assert result["status"] == Status.FAILED
        assert result["job_id"] == job.id
        assert job.status == Status.FAILED
        assert job.stderr.get("error:ear-clipping:message") == "No valid ear found for polygon"
        assert job.stderr.get("error:ear-clipping:type") == "EarClippingFailureError"
        mock_repo.save.assert_called_once_with(job)
        mock_tasks_queue.put.assert_not_called()

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_execute_art_gallery_step_broadcast_starts_first_child(self, mock_repo_cls, mock_state_repo_cls, mock_queue):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        mock_repo.exists.return_value = False
        job = Job(
            id=Identifier("parent-1"),
            step_name=StepName.ART_GALLERY,
            stdin={"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []},
            stdout={},
            children_ids=[],
            parent_id=None,
        )
        mock_repo.get.return_value = job
        task = StartTask()
        req = {"job_id": Identifier("parent-1"), "user_email": Email("u@e.com")}
        task.handler(req)
        assert len(job.children_ids) == 5
        put_calls = mock_queue.put.call_args_list
        assert len(put_calls) >= 2
        actions = [put_calls[i][0][0].action for i in range(len(put_calls))]
        assert Action.REPORT in actions
        assert Action.START in actions
        start_msg = next(m for m in (put_calls[i][0][0] for i in range(len(put_calls))) if m.action == Action.START)
        assert start_msg.job_id == job.children_ids[0]

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_execute_suspended_step_requeues_and_saves_job(
        self, mock_repo_cls, mock_state_repo_cls, mock_tasks_queue
    ):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.STITCHING,
            status=Status.PENDING,
            meta={},
        )
        mock_repo.get.return_value = job
        task = StartTask()
        req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
        with patch.object(
            StartTask,
            "execute",
            side_effect=SuspendedStepError("Step suspended", state={"resume": "data"}),
        ):
            result = task.handler(req)
        assert result["status"] == Status.PENDING
        assert result["job_id"] == job.id
        mock_repo.save.assert_called_once_with(job)
        assert job.meta.get("step:stitching:attempt") == 1
        mock_tasks_queue.put.assert_called_once()

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_execute_suspended_step_at_max_attempts_fails_job_and_saves(
        self, mock_repo_cls, mock_state_repo_cls, mock_tasks_queue
    ):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        job = Job(
            id=Identifier("j1"),
            step_name=StepName.STITCHING,
            status=Status.PENDING,
            meta={},
        )
        mock_repo.get.return_value = job
        # resume() will load state with attempt=10 (max); requeue() -> flush() would do attempt+1 and raise
        mock_state_repo_cls.return_value.get.return_value = JobState(
            id=job.id, data={}, attempt=Attempt(10)
        )
        task = StartTask()
        req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
        with patch("attributes.MAX_TASK_CONTINUATION_STEPS", 10), patch.object(
            StartTask,
            "execute",
            side_effect=SuspendedStepError("Step suspended", state={"resume": "data"}),
        ):
            result = task.handler(req)
        assert result["status"] == Status.FAILED
        assert result["job_id"] == job.id
        assert job.status == Status.FAILED
        mock_repo.save.assert_called_once_with(job)
        mock_tasks_queue.put.assert_not_called()


class TestReportTask:
    """Test ReportTask validate and execute with mocks."""

    def test_validate_returns_task_request(self):
        task = ReportTask()
        req = task.validate({"job_id": "j1", "user_email": "u@e.com"})
        assert req["job_id"] == Identifier("j1")
        assert req["user_email"] == Email("u@e.com")

    @patch("tasks.queue")
    @patch("tasks.JobsRepository")
    def test_execute_job_failed_notifies_parent(self, mock_repo_cls, mock_queue):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        job = MagicMock()
        job.is_failed.return_value = True
        job.parent_id = Identifier("parent-1")
        job.id = Identifier("j1")
        mock_repo.get.return_value = job
        task = ReportTask()
        req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
        result = task.handler(req)
        assert result["status"] == Status.FAILED
        # Handler returns early when job is failed; execute() and broadcast() are not called.
        mock_queue.put.assert_not_called()

    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_execute_children_all_success_sets_status_success_and_notifies(
        self, mock_repo_cls, mock_state_repo_cls, mock_queue
    ):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        parent = Job(
            id=Identifier("p1"),
            parent_id=Identifier("grandparent"),
            children_ids=[Identifier("c1")],
            status=Status.PENDING,
            step_name=StepName.ART_GALLERY,
            stdout={},
            stderr={},
            meta={},
        )
        child = MagicMock()
        child.is_failed.return_value = False
        child.is_pending.return_value = False
        child.stdout = {"out": "c1"}
        child.stderr = {}
        mock_repo.get.side_effect = lambda id: parent if id == Identifier("p1") else child
        task = ReportTask()
        req = {"job_id": Identifier("p1"), "user_email": Email("u@e.com")}
        result = task.handler(req)
        assert result["status"] == Status.SUCCESS
        assert parent.status == Status.SUCCESS
        finished_at_key = "step:art-gallery:finished_at"
        assert finished_at_key in parent.meta
        assert isinstance(parent.meta[finished_at_key], str)
        assert "T" in parent.meta[finished_at_key]
        mock_repo.save.assert_called_once()
        mock_queue.put.assert_called_once()

    @patch("tasks.ReportTask.broadcast")
    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_execute_any_child_failed_merges_stderr_sets_failed(
        self, mock_repo_cls, mock_state_repo_cls, mock_queue, mock_broadcast
    ):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        parent = Job(
            id=Identifier("p1"),
            parent_id=None,
            children_ids=[Identifier("c1")],
            status=Status.PENDING,
            step_name=StepName.ART_GALLERY,
        )
        child = MagicMock()
        child.is_failed.return_value = True
        child.is_pending.return_value = False
        child.stdout = {}
        child.stderr = {"err": "failed"}
        mock_repo.get.side_effect = lambda rid: parent if str(rid) == "p1" else child
        task = ReportTask()
        req = {"job_id": Identifier("p1"), "user_email": Email("u@e.com")}
        task.handler(req)
        assert parent.status == Status.FAILED
        assert parent.stderr.get("err") == "failed"
        assert "error:art-gallery:message" in parent.stderr
        assert "error:art-gallery:type" in parent.stderr

    @patch("tasks.ReportTask.broadcast")
    @patch("tasks.queue")
    @patch("tasks.JobStateRepository")
    @patch("tasks.JobsRepository")
    def test_execute_merges_children_meta_into_parent(
        self, mock_repo_cls, mock_state_repo_cls, mock_queue, mock_broadcast
    ):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_state_repo_cls.return_value.get.side_effect = RecordNotFoundError("")
        parent = Job(
            id=Identifier("p1"),
            parent_id=None,
            children_ids=[Identifier("c1")],
            status=Status.PENDING,
            step_name=StepName.ART_GALLERY,
            meta={"step:art-gallery:started_at": "2026-03-02T01:00:00"},
        )
        child = Job(
            id=Identifier("c1"),
            parent_id=Identifier("p1"),
            children_ids=[],
            status=Status.SUCCESS,
            step_name=StepName.EAR_CLIPPING,
            stdout={"triangles": []},
            meta={
                "step:ear-clipping:started_at": "2026-03-02T01:00:05",
                "step:ear-clipping:finished_at": "2026-03-02T01:00:10",
            },
        )
        mock_repo.get.side_effect = lambda rid: parent if str(rid) == "p1" else child
        task = ReportTask()
        req = {"job_id": Identifier("p1"), "user_email": Email("u@e.com")}
        task.handler(req)
        assert parent.status == Status.SUCCESS
        assert parent.stdout == {"triangles": []}
        assert parent.meta["step:art-gallery:started_at"] == "2026-03-02T01:00:00"
        assert parent.meta["step:ear-clipping:started_at"] == "2026-03-02T01:00:05"
        assert parent.meta["step:ear-clipping:finished_at"] == "2026-03-02T01:00:10"
        assert "step:art-gallery:finished_at" in parent.meta
        assert isinstance(parent.duration, Duration)
        assert parent.duration >= 0
