"""Tests for messages package."""

from messages import Message


class TestMessage:
    """Test Message (SQS message shape)."""

    def test_message_unserialize_minimal(self):
        m = Message.unserialize({
            "job_id": "job-123",
            "user_email": "user@example.com",
            "receipt_handle": "rh1",
        })
        assert m.receipt_handle is not None
        assert str(m.receipt_handle) == "rh1"
        assert str(m.job_id) == "job-123"
        assert str(m.user_email) == "user@example.com"
