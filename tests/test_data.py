"""Tests for data package."""

import json
from unittest.mock import MagicMock
from unittest.mock import patch

import data
import pytest
from attributes import Offset
from data import Bucket
from data import Page
from data import Secret
from exceptions import ConfigurationError
from exceptions import NotFoundError
from exceptions import ServiceUnavailableError
from exceptions import StorageError
from exceptions import ValidationError

# Load api package first to avoid circular import (api.api -> data -> api.logger -> api)
import api  # noqa: F401


class TestPage:
    """Test Page (search results with pagination)."""

    def test_empty_page(self):
        p = Page()
        assert list(p) == []
        assert p.continues is False
        assert len(p) == 0

    def test_page_with_keys(self):
        p = Page(keys=["a", "b"], next_token=None)
        assert list(p) == ["a", "b"]
        assert p.continues is False

    def test_page_continues(self):
        p = Page(keys=[], next_token=Offset("token"))
        assert p.continues is True


class TestOffset:
    """Test Offset attribute."""

    def test_valid(self):
        assert Offset("abc") == "abc"

    def test_none_raises(self):
        from exceptions import ValidationError

        with pytest.raises(ValidationError):
            Offset(None)

    def test_empty_raises(self):
        from exceptions import ValidationError

        with pytest.raises(ValidationError):
            Offset("   ")


class TestBucket:
    """Test Bucket (S3 operations)."""

    def test_name_uses_env(self):
        b = Bucket()
        assert b.name == "test-data-bucket"

    def test_name_missing_raises(self):
        with patch("data.DATA_BUCKET_NAME", ""):
            b = Bucket()
            with pytest.raises(ConfigurationError, match="DATA_BUCKET_NAME"):
                _ = b.name

    def test_client_lazy(self):
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = MagicMock()
            b = Bucket()
            _ = b.client
            _ = b.client
            mock_boto.client.assert_called_once_with("s3")

    def test_exists_invalid_key_raises(self):
        b = Bucket()
        with pytest.raises(ValidationError, match="non-empty string"):
            b.exists("")
        with pytest.raises(ValidationError, match="non-empty string"):
            b.exists(None)
        with pytest.raises(ValidationError, match="non-empty string"):
            b.exists(123)

    def test_exists_true(self):
        mock_client = MagicMock()
        mock_client.head_object.return_value = {}
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            assert b.exists("data/k.json") is True
            mock_client.head_object.assert_called_once()
            call_kw = mock_client.head_object.call_args[1]
            assert call_kw["Key"] == "data/k.json"

    def test_exists_404_false(self):
        mock_client = MagicMock()
        mock_client.head_object.side_effect = data.ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadObject")
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            assert b.exists("data/missing.json") is False

    def test_exists_other_client_error_raises(self):
        mock_client = MagicMock()
        mock_client.head_object.side_effect = data.ClientError({"Error": {"Code": "500", "Message": "Server Error"}}, "HeadObject")
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ServiceUnavailableError, match="S3"):
                b.exists("data/k.json")

    def test_load_invalid_key_raises(self):
        b = Bucket()
        with pytest.raises(ValidationError, match="non-empty string"):
            b.load("")
        with pytest.raises(ValidationError, match="non-empty string"):
            b.load(None)

    def test_load_success(self):
        mock_client = MagicMock()
        mock_body = MagicMock()
        mock_body.read.return_value = b'{"a": 1}'
        mock_client.get_object.return_value = {"Body": mock_body}
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            data = b.load("data/k.json")
            assert data == {"a": 1}

    def test_load_missing_body_raises(self):
        mock_client = MagicMock()
        mock_client.get_object.return_value = {}
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ValidationError, match="missing Body"):
                b.load("data/k.json")

    def test_load_empty_content_raises(self):
        mock_client = MagicMock()
        mock_body = MagicMock()
        mock_body.read.return_value = b"   \n"
        mock_client.get_object.return_value = {"Body": mock_body}
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ValidationError, match="Empty content"):
                b.load("data/k.json")

    def test_load_no_such_key_returns_default(self):
        mock_client = MagicMock()
        mock_client.get_object.side_effect = data.ClientError({"Error": {"Code": "NoSuchKey", "Message": "Not Found"}}, "GetObject")
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            assert b.load("data/missing.json", default=None) is None
            assert b.load("data/missing.json", default={}) == {}

    def test_load_other_client_error_raises(self):
        mock_client = MagicMock()
        mock_client.get_object.side_effect = data.ClientError({"Error": {"Code": "500", "Message": "Error"}}, "GetObject")
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ServiceUnavailableError, match="S3"):
                b.load("data/k.json")

    def test_load_invalid_json_raises(self):
        mock_client = MagicMock()
        mock_body = MagicMock()
        mock_body.read.return_value = b"not json"
        mock_client.get_object.return_value = {"Body": mock_body}
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ValidationError, match="Invalid JSON"):
                b.load("data/k.json")

    def test_load_invalid_utf8_raises(self):
        mock_client = MagicMock()
        mock_body = MagicMock()
        mock_body.read.return_value = b"\xff\xfe"
        mock_client.get_object.return_value = {"Body": mock_body}
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ValidationError, match="Invalid UTF-8"):
                b.load("data/k.json")

    def test_save_invalid_key_raises(self):
        b = Bucket()
        with pytest.raises(ValidationError, match="non-empty string"):
            b.save("", {})
        with pytest.raises(ValidationError, match="non-empty string"):
            b.save(None, {})

    def test_save_success(self):
        mock_client = MagicMock()
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            b.save("data/k.json", {"x": 1})
            mock_client.put_object.assert_called_once()
            call_kw = mock_client.put_object.call_args[1]
            assert call_kw["Key"] == "data/k.json"
            assert json.loads(call_kw["Body"].decode("utf-8")) == {"x": 1}

    def test_save_not_serializable_raises(self):
        mock_client = MagicMock()
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ValidationError, match="not JSON serializable"):
                b.save("data/k.json", object())

    def test_save_client_error_raises(self):
        mock_client = MagicMock()
        mock_client.put_object.side_effect = data.ClientError({"Error": {"Code": "500", "Message": "Error"}}, "PutObject")
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ServiceUnavailableError, match="S3"):
                b.save("data/k.json", {})

    def test_delete_invalid_key_raises(self):
        b = Bucket()
        with pytest.raises(ValidationError, match="non-empty string"):
            b.delete("")

    def test_delete_success(self):
        mock_client = MagicMock()
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            assert b.delete("data/k.json") is True
            mock_client.delete_object.assert_called_once()
            assert mock_client.delete_object.call_args[1]["Key"] == "data/k.json"

    def test_delete_no_such_key_returns_false(self):
        mock_client = MagicMock()
        mock_client.delete_object.side_effect = data.ClientError({"Error": {"Code": "NoSuchKey", "Message": "Not Found"}}, "DeleteObject")
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            assert b.delete("data/missing.json") is False

    def test_delete_other_client_error_raises(self):
        mock_client = MagicMock()
        mock_client.delete_object.side_effect = data.ClientError({"Error": {"Code": "500", "Message": "Error"}}, "DeleteObject")
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ServiceUnavailableError, match="S3"):
                b.delete("data/k.json")

    def test_search_invalid_prefix_raises(self):
        b = Bucket()
        with pytest.raises(ValidationError, match="Prefix must be a string"):
            b.search(prefix=123)

    def test_search_success_no_truncation(self):
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "data/a.json"}, {"Key": "data/b.json"}],
            "IsTruncated": False,
        }
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            page = b.search(prefix="data/", limit=10)
            assert list(page.keys) == ["data/a.json", "data/b.json"]
            assert page.next_token is None

    def test_search_with_next_token(self):
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {
            "Contents": [{"Key": "data/c.json"}],
            "IsTruncated": True,
            "NextContinuationToken": "token123",
        }
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            page = b.search(prefix="data/", limit=1, next_token=Offset("prev"))
            assert list(page.keys) == ["data/c.json"]
            assert str(page.next_token) == "token123"

    def test_search_client_error_raises(self):
        mock_client = MagicMock()
        mock_client.list_objects_v2.side_effect = data.ClientError({"Error": {"Code": "500", "Message": "Error"}}, "ListObjectsV2")
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(ServiceUnavailableError, match="S3"):
                b.search(prefix="data/")

    def test_search_non_dict_response_raises(self):
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = "not a dict"
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            with pytest.raises(StorageError, match="expected dictionary"):
                b.search(prefix="data/")

    def test_search_no_contents(self):
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {"IsTruncated": False}
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            page = b.search(prefix="empty/")
            assert list(page.keys) == []
            assert page.next_token is None

    def test_search_limit_from_int(self):
        mock_client = MagicMock()
        mock_client.list_objects_v2.return_value = {"IsTruncated": False}
        with patch("data.boto3") as mock_boto:
            mock_boto.client.return_value = mock_client
            b = Bucket()
            b.search(prefix="data/", limit=5)
            mock_client.list_objects_v2.assert_called_once()
            assert mock_client.list_objects_v2.call_args[1]["MaxKeys"] == 5


class TestSecret:
    """Test Secret (S3-backed secrets)."""

    def test_get_invalid_id_raises(self):
        with pytest.raises(ValidationError, match="Secret ID"):
            Secret.get("")
        with pytest.raises(ValidationError, match="Secret ID"):
            Secret.get(None)
        with pytest.raises(ValidationError, match="Secret ID"):
            Secret.get(123)

    def test_get_success_and_cached(self):
        with patch("data.Secret._get_bucket_name", return_value="secrets-bucket"):
            mock_client = MagicMock()
            mock_body = MagicMock()
            mock_body.read.return_value = b"secret-value"
            mock_client.get_object.return_value = {"Body": mock_body}
            with patch("data.Secret._get_client", return_value=mock_client):
                Secret._cache.clear()
                val = Secret.get("JWT_SECRET")
                assert val == "secret-value"
                assert Secret._cache.get("JWT_SECRET") == "secret-value"
                val2 = Secret.get("JWT_SECRET")
                assert val2 == "secret-value"
                mock_client.get_object.assert_called_once()
                Secret._cache.clear()

    def test_get_empty_content_raises(self):
        with patch("data.Secret._get_bucket_name", return_value="secrets-bucket"):
            mock_client = MagicMock()
            mock_body = MagicMock()
            mock_body.read.return_value = b"   "
            mock_client.get_object.return_value = {"Body": mock_body}
            with patch("data.Secret._get_client", return_value=mock_client):
                Secret._cache.clear()
                with pytest.raises(NotFoundError, match="empty"):
                    Secret.get("EMPTY_SECRET")
                Secret._cache.clear()

    def test_get_no_such_key_raises(self):
        with patch("data.Secret._get_bucket_name", return_value="secrets-bucket"):
            mock_client = MagicMock()
            mock_client.get_object.side_effect = data.ClientError({"Error": {"Code": "NoSuchKey", "Message": "Not Found"}}, "GetObject")
            with patch("data.Secret._get_client", return_value=mock_client):
                Secret._cache.clear()
                with pytest.raises(NotFoundError, match="not found"):
                    Secret.get("MISSING")
                Secret._cache.clear()

    def test_get_other_client_error_raises(self):
        with patch("data.Secret._get_bucket_name", return_value="secrets-bucket"):
            mock_client = MagicMock()
            mock_client.get_object.side_effect = data.ClientError({"Error": {"Code": "500", "Message": "Error"}}, "GetObject")
            with patch("data.Secret._get_client", return_value=mock_client):
                Secret._cache.clear()
                with pytest.raises(ServiceUnavailableError, match="S3"):
                    Secret.get("FAIL")
                Secret._cache.clear()

    def test_get_bucket_name_missing_raises(self):
        with patch("data.SECRETS_BUCKET_NAME", ""):
            with pytest.raises(ConfigurationError, match="SECRETS_BUCKET_NAME"):
                Secret._get_bucket_name()
