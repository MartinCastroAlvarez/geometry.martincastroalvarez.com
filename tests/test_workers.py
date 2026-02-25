"""Tests for workers package."""

import pytest

from attributes import Identifier
from enums import Status

from workers import WorkerRequest
from workers import WorkerResponse


class TestWorkerRequest:
    """Test WorkerRequest parsing."""

    def test_request_has_action_and_body(self):
        req = WorkerRequest.unserialize(
            {"action": "start", "job_id": "j1", "user_email": "u@e.com", "receipt_handle": "rh1"}
        )
        assert req.action.value == "start"
        assert str(req.job_id) == "j1"
        assert str(req.user_email) == "u@e.com"


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
