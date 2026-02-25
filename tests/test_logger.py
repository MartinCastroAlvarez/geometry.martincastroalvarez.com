"""Tests for api logger (get_logger, log_extra, configure_logging)."""

from api.logger import configure_logging
from api.logger import get_logger
from api.logger import log_extra


class TestGetLogger:
    def test_returns_logger(self):
        log = get_logger("test.module")
        assert log.name == "test.module"


class TestLogExtra:
    def test_empty(self):
        assert log_extra() == {}

    def test_request_id_path_method(self):
        e = log_extra(request_id="req-1", path="/v1/jobs", method="GET")
        assert e["request_id"] == "req-1"
        assert e["path"] == "/v1/jobs"
        assert e["method"] == "GET"

    def test_kwargs_passed_through(self):
        e = log_extra(elapsed_ms=100)
        assert e["elapsed_ms"] == 100


class TestConfigureLogging:
    def test_does_not_raise(self):
        configure_logging()
