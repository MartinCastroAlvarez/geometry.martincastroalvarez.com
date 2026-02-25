"""Tests for tasks package."""

from enums import Status

from tasks.response import TaskResponse


class TestTaskResponse:
    """Test task response types."""

    def test_task_response_typed(self):
        r: TaskResponse = {"status": Status.SUCCESS}
        assert r["status"] == Status.SUCCESS
