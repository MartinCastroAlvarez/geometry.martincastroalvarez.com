"""Tests for messages package."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from enums import Action
from exceptions import ConfigurationError
from exceptions import InternalServerError
from exceptions import ValidationError
from messages import Message
from messages import Queue


class TestMessage:
    """Test Message (SQS message shape)."""

    def test_message_unserialize_minimal(self):
        m = Message.unserialize(
            {
                "job_id": "job-123",
                "user_email": "user@example.com",
                "receipt_handle": "rh1",
            }
        )
        assert m.receipt_handle is not None
        assert str(m.receipt_handle) == "rh1"
        assert str(m.job_id) == "job-123"
        assert str(m.user_email) == "user@example.com"

    def test_message_unserialize_non_dict_raises(self):
        with pytest.raises(ValidationError, match="dictionary"):
            Message.unserialize([])

    def test_message_unserialize_with_meta(self):
        m = Message.unserialize(
            {
                "action": "start",
                "job_id": "j1",
                "user_email": "u@e.com",
                "meta": {"key": "value"},
            }
        )
        assert m.meta == {"key": "value"}
        assert m.action == Action.START

    def test_message_serialize_includes_meta_when_present(self):
        m = Message(action=Action.START, job_id="j1", user_email="u@e.com", meta={"k": "v"})
        d = m.serialize()
        assert d["action"] == "start"
        assert d["meta"] == {"k": "v"}

    def test_message_serialize_omits_meta_when_none(self):
        m = Message(action=Action.START, job_id="j1", user_email="u@e.com")
        d = m.serialize()
        assert "meta" not in d

    def test_message_post_init_coerces_action_str(self):
        m = Message(action="start", job_id="j1", user_email="u@e.com")
        assert m.action == Action.START

    def test_message_post_init_coerces_receipt_handle_str(self):
        m = Message(action=Action.START, job_id="j1", user_email="u@e.com", receipt_handle="rh-x")
        assert str(m.receipt_handle) == "rh-x"

    def test_message_post_init_meta_non_dict_coerced(self):
        m = Message(action=Action.START, job_id="j1", user_email="u@e.com", meta=[("k", "v")])
        assert m.meta == {"k": "v"}


class TestQueue:
    """Test Queue (SQS) with mocked client."""

    @patch("messages.QUEUE_NAME", None)
    def test_queue_name_missing_raises(self):
        q = Queue()
        with pytest.raises(ConfigurationError, match="QUEUE_NAME"):
            _ = q.name

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_url_returns_queue_url(self, mock_boto3):
        mock_client = MagicMock()
        mock_client.get_queue_url.return_value = {"QueueUrl": "https://sqs.region.amazonaws.com/123/my-queue"}
        mock_boto3.client.return_value = mock_client
        q = Queue()
        url = q.url
        assert url == "https://sqs.region.amazonaws.com/123/my-queue"

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_url_client_error_raises_internal_server_error(self, mock_boto3):
        from botocore.exceptions import ClientError

        mock_client = MagicMock()
        mock_client.get_queue_url.side_effect = ClientError({"Error": {"Code": "500"}}, "get_queue_url")
        mock_boto3.client.return_value = mock_client
        q = Queue()
        with pytest.raises(InternalServerError, match="unavailable"):
            _ = q.url

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_put_success_returns_message_id(self, mock_boto3):
        mock_client = MagicMock()
        mock_client.get_queue_url.return_value = {"QueueUrl": "https://q"}
        mock_client.send_message.return_value = {"MessageId": "mid-123"}
        mock_boto3.client.return_value = mock_client
        q = Queue()
        msg = Message(action=Action.START, job_id="j1", user_email="u@e.com")
        mid = q.put(msg)
        assert mid == "mid-123"

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_put_with_delay(self, mock_boto3):
        mock_client = MagicMock()
        mock_client.get_queue_url.return_value = {"QueueUrl": "https://q"}
        mock_client.send_message.return_value = {"MessageId": "mid-1"}
        mock_boto3.client.return_value = mock_client
        q = Queue()
        msg = Message(action=Action.REPORT, job_id="j1", user_email="u@e.com")
        q.put(msg, delay_seconds=60)
        call_kw = mock_client.send_message.call_args[1]
        assert call_kw["DelaySeconds"] == 60

    def test_queue_put_non_message_raises(self):
        q = Queue()
        with pytest.raises(ValidationError, match="Message"):
            q.put({"action": "start"})  # type: ignore

    def test_queue_put_delay_invalid_raises(self):
        with patch("messages.QUEUE_NAME", "q"):
            q = Queue()
            msg = Message(action=Action.START, job_id="j1", user_email="u@e.com")
            with pytest.raises(ValidationError, match="Delay"):
                q.put(msg, delay_seconds=1000)

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_put_client_error_raises_internal_server_error(self, mock_boto3):
        from botocore.exceptions import ClientError

        mock_client = MagicMock()
        mock_client.get_queue_url.return_value = {"QueueUrl": "https://q"}
        mock_client.send_message.side_effect = ClientError({"Error": {"Code": "500"}}, "send_message")
        mock_boto3.client.return_value = mock_client
        q = Queue()
        msg = Message(action=Action.START, job_id="j1", user_email="u@e.com")
        with pytest.raises(InternalServerError, match="unavailable"):
            q.put(msg)

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_receive_success_returns_messages(self, mock_boto3):
        mock_client = MagicMock()
        mock_client.get_queue_url.return_value = {"QueueUrl": "https://q"}
        mock_client.receive_message.return_value = {"Messages": [{"Body": "{}", "ReceiptHandle": "rh1"}]}
        mock_boto3.client.return_value = mock_client
        q = Queue()
        msgs = q.receive(max_messages=1)
        assert len(msgs) == 1
        assert msgs[0]["ReceiptHandle"] == "rh1"

    @patch("messages.QUEUE_NAME", "my-queue")
    def test_queue_receive_max_messages_invalid_raises(self):
        q = Queue()
        with pytest.raises(ValidationError, match="Max messages"):
            q.receive(max_messages=0)
        with pytest.raises(ValidationError, match="Max messages"):
            q.receive(max_messages=100)

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_receive_client_error_raises(self, mock_boto3):
        from botocore.exceptions import ClientError

        mock_client = MagicMock()
        mock_client.get_queue_url.return_value = {"QueueUrl": "https://q"}
        mock_client.receive_message.side_effect = ClientError({"Error": {}}, "receive_message")
        mock_boto3.client.return_value = mock_client
        q = Queue()
        with pytest.raises(InternalServerError):
            q.receive()

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_delete_success(self, mock_boto3):
        mock_client = MagicMock()
        mock_client.get_queue_url.return_value = {"QueueUrl": "https://q"}
        mock_boto3.client.return_value = mock_client
        q = Queue()
        q.delete("rh-123")
        mock_client.delete_message.assert_called_once_with(QueueUrl="https://q", ReceiptHandle="rh-123")

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_commit_no_receipt_handle_no_op(self, mock_boto3):
        q = Queue()
        msg = Message(action=Action.START, job_id="j1", user_email="u@e.com", receipt_handle=None)
        q.commit(msg)
        mock_boto3.client.assert_not_called()

    @patch("messages.QUEUE_NAME", "my-queue")
    @patch("messages.boto3")
    def test_queue_commit_with_receipt_handle_calls_delete(self, mock_boto3):
        mock_client = MagicMock()
        mock_client.get_queue_url.return_value = {"QueueUrl": "https://q"}
        mock_boto3.client.return_value = mock_client
        q = Queue()
        msg = Message(action=Action.START, job_id="j1", user_email="u@e.com", receipt_handle="rh-1")
        q.commit(msg)
        mock_client.delete_message.assert_called_once()
