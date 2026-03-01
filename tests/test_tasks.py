"""Tests for tasks package."""

from unittest.mock import MagicMock
from unittest.mock import patch

from attributes import Email
from attributes import Identifier
from enums import Status
from enums import StepName
from models import Job

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

    def test_handler_body_none_defaults_to_empty_dict(self):
        with patch.object(StartTask, "validate", return_value={"job_id": Identifier("j1"), "user_email": Email("u@e.com")}) as mock_validate:
            with patch.object(StartTask, "execute", return_value={"status": Status.SUCCESS, "job_id": Identifier("j1")}) as mock_execute:
                task = StartTask()
                task.handler(body=None)
                mock_validate.assert_called_once_with({})
                mock_execute.assert_called_once()


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
        result = task.execute(req)
        assert result["status"] == Status.FAILED
        assert result["reason"] == "job_failed"
        mock_queue.put.assert_not_called()

    @patch("tasks.queue")
    @patch("tasks.JobsRepository")
    def test_execute_unknown_step_returns_failed(self, mock_repo_cls, mock_queue):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        job = MagicMock()
        job.is_failed.return_value = False
        job.step_name = "unknown_step_name"
        job.id = Identifier("j1")
        mock_repo.get.return_value = job
        with patch("tasks.STEP_CLASS_BY_NAME", {}):
            task = StartTask()
            req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
            result = task.execute(req)
        assert result["status"] == Status.FAILED
        assert result["reason"] == "unknown_step"

    @patch("tasks.queue")
    @patch("tasks.JobsRepository")
    def test_execute_success_enqueues_report_for_non_art_gallery_step(self, mock_repo_cls, mock_queue):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        job = MagicMock()
        job.is_failed.return_value = False
        job.step_name = StepName.VISIBILITY_MATRIX
        job.id = Identifier("j1")
        job.stdout = {}
        mock_repo.get.return_value = job
        step_instance = MagicMock()
        step_instance.run.return_value = {"step:visibility_matrix": "success"}
        step_instance.job = job
        with patch.dict("tasks.STEP_CLASS_BY_NAME", {StepName.VISIBILITY_MATRIX: lambda **kw: step_instance}):
            task = StartTask()
            req = {"job_id": Identifier("j1"), "user_email": Email("u@e.com")}
            result = task.execute(req)
        assert result["status"] == Status.SUCCESS
        mock_queue.put.assert_called_once()
        mock_repo.save.assert_called_once()


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
        result = task.execute(req)
        assert result["status"] == Status.FAILED
        mock_queue.put.assert_called_once()

    @patch("tasks.queue")
    @patch("tasks.JobsRepository")
    def test_execute_children_all_success_sets_status_success_and_notifies(self, mock_repo_cls, mock_queue):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        parent = MagicMock()
        parent.is_failed.return_value = False
        parent.is_pending.return_value = False
        parent.id = Identifier("p1")
        parent.parent_id = Identifier("grandparent")
        parent.children_ids = [Identifier("c1")]
        parent.stdout = {}
        parent.stderr = {}
        child = MagicMock()
        child.is_failed.return_value = False
        child.is_pending.return_value = False
        child.stdout = {"out": "c1"}
        child.stderr = {}
        mock_repo.get.side_effect = lambda id: parent if id == Identifier("p1") else child
        task = ReportTask()
        req = {"job_id": Identifier("p1"), "user_email": Email("u@e.com")}
        result = task.execute(req)
        assert result["status"] == Status.SUCCESS
        assert parent.status == Status.SUCCESS
        mock_repo.save.assert_called_once()
        mock_queue.put.assert_called_once()

    @patch("tasks.ReportTask.notify")
    @patch("tasks.queue")
    @patch("tasks.JobsRepository")
    def test_execute_any_child_failed_merges_stderr_sets_failed(self, mock_repo_cls, mock_queue, mock_notify):
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
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
        task.execute(req)
        assert parent.status == Status.FAILED
        assert parent.stderr == {"err": "failed"}
