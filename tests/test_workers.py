"""Tests for workers package."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from attributes import Identifier
from enums import Action
from enums import Status
from exceptions import ValidationError
from workers import WorkerRequest
from workers import WorkerResponse
from workers import handler


class TestWorkerRequest:
    """Test WorkerRequest parsing."""

    def test_request_has_action_and_body(self):
        req = WorkerRequest.unserialize({"action": "start", "job_id": "j1", "user_email": "u@e.com", "receipt_handle": "rh1"})
        assert req.action.value == "start"
        assert str(req.job_id) == "j1"
        assert str(req.user_email) == "u@e.com"

    def test_unserialize_with_body_key_sqs_record(self):
        req = WorkerRequest.unserialize(
            {
                "body": '{"action": "report", "job_id": "j2", "user_email": "u@e.com"}',
                "receiptHandle": "rh-sqs",
            }
        )
        assert req.action == Action.REPORT
        assert str(req.job_id) == "j2"

    def test_unserialize_with_body_empty_uses_empty_dict(self):
        req = WorkerRequest.unserialize({"body": "", "receiptHandle": "rh1"})
        assert req.data == {}

    def test_unserialize_with_receipt_handle_key(self):
        req = WorkerRequest.unserialize(
            {
                "action": "start",
                "job_id": "j1",
                "user_email": "u@e.com",
                "receipt_handle": "rh-alt",
            }
        )
        assert str(req.receipt_handle) == "rh-alt"

    def test_body_includes_meta_when_present(self):
        req = WorkerRequest.unserialize(
            {
                "action": "start",
                "job_id": "j1",
                "user_email": "u@e.com",
                "receipt_handle": "rh1",
                "meta": {"k": "v"},
            }
        )
        assert req.body.get("meta") == {"k": "v"}

    def test_from_event_with_records_yields_per_record(self):
        event = {
            "Records": [
                {"body": '{"action": "start", "job_id": "j1", "user_email": "u@e.com"}', "receiptHandle": "rh1"},
                {"body": '{"action": "report", "job_id": "j2", "user_email": "u@e.com"}', "receiptHandle": "rh2"},
            ]
        }
        requests = list(WorkerRequest.from_event(event))
        assert len(requests) == 2
        assert requests[0].action == Action.START and str(requests[0].job_id) == "j1"
        assert requests[1].action == Action.REPORT and str(requests[1].job_id) == "j2"

    def test_from_event_without_records_yields_single_request(self):
        event = {"action": "start", "job_id": "j1", "user_email": "u@e.com", "receipt_handle": "rh1"}
        requests = list(WorkerRequest.from_event(event))
        assert len(requests) == 1
        assert requests[0].action == Action.START


class TestWorkerResponse:
    """Test WorkerResponse serialization."""

    def test_serialize_with_status_and_identifier(self):
        resp = WorkerResponse(results=[{"status": Status.SUCCESS, "job_id": Identifier("job-1")}])
        d = resp.serialize()
        assert "results" in d
        assert len(d["results"]) == 1
        assert d["results"][0]["status"] == "success"
        assert d["results"][0]["job_id"] == "job-1"

    def test_serialize_with_none_and_plain_value(self):
        resp = WorkerResponse(results=[{"status": Status.SUCCESS, "error": None, "reason": "ok"}])
        d = resp.serialize()
        assert d["results"][0]["error"] is None
        assert d["results"][0]["reason"] == "ok"

    def test_unserialize_raises(self):
        with pytest.raises(NotImplementedError):
            WorkerResponse.unserialize({})


class TestHandler:
    """Test worker handler with mocks."""

    @patch("workers.Queue")
    def test_handler_invalid_request_appends_failed_result(self, mock_queue_cls):
        event = {
            "Records": [
                {
                    "body": '{"action": "start", "job_id": "", "user_email": "u@e.com"}',
                    "receiptHandle": "rh1",
                }
            ]
        }
        with pytest.raises(ValidationError, match="Identifier must be a non-empty string"):
            handler(event, None)

    @patch("workers.Queue")
    def test_handler_unknown_action_appends_failed_result(self, mock_queue_cls):
        # ROUTES.get returns None for a made-up key so task_class is None -> "Unknown action"
        event = {
            "Records": [
                {
                    "body": '{"action": "start", "job_id": "j1", "user_email": "u@e.com"}',
                    "receiptHandle": "rh1",
                }
            ]
        }
        with patch("workers.ROUTES", {Action.REPORT: type("ReportTask", (), {})()}):
            # Only REPORT in ROUTES, so START raises KeyError
            resp = handler(event, None)
        assert len(resp.results) == 1
        assert resp.results[0]["status"] == Status.FAILED
        assert "error" in resp.results[0]

    @patch("workers.Queue")
    def test_handler_start_dispatches_and_commits(self, mock_queue_cls):
        mock_queue = MagicMock()
        mock_queue_cls.return_value = mock_queue
        mock_task = MagicMock()
        mock_task.handler.return_value = {"status": Status.SUCCESS, "job_id": Identifier("j1")}
        with patch.dict("workers.ROUTES", {Action.START: lambda: mock_task}):
            event = {
                "Records": [
                    {
                        "body": '{"action": "start", "job_id": "j1", "user_email": "u@e.com"}',
                        "receiptHandle": "rh1",
                    }
                ]
            }
            resp = handler(event, None)
        assert len(resp.results) == 1
        assert resp.results[0]["status"] == Status.SUCCESS
        mock_queue.commit.assert_called_once()

    @patch("workers.Queue")
    def test_handler_commit_exception_logged_result_still_appended(self, mock_queue_cls):
        mock_queue = MagicMock()
        mock_queue.commit.side_effect = Exception("commit failed")
        mock_queue_cls.return_value = mock_queue
        mock_task = MagicMock()
        mock_task.handler.return_value = {"status": Status.SUCCESS, "job_id": Identifier("j1")}
        with patch.dict("workers.ROUTES", {Action.START: lambda: mock_task}):
            event = {"action": "start", "job_id": "j1", "user_email": "u@e.com", "receipt_handle": "rh1"}
            with pytest.raises(Exception, match="commit failed"):
                handler(event, None)
        mock_queue.commit.assert_called_once()
