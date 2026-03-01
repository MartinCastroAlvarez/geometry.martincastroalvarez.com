"""Tests for queries package."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import api  # noqa: F401

from data import Page
from models import ArtGallery
from models import Job
from models import User
from queries import ArtGalleryDetailsQuery
from queries import ArtGalleryListQuery
from queries import JobDetailsQuery
from queries import JobListQuery
from queries import ListQuery
from queries import Query


class TestQueryBase:
    """Test base Query class."""

    def test_query_raises_not_implemented(self):
        """Base Query.query() raises NotImplementedError when subclass does not override query()."""
        class MinimalQuery(Query):
            def validate(self, body):
                return {}

        q = MinimalQuery()
        with pytest.raises(NotImplementedError):
            q.execute(q.validate({}))

    def test_execute_delegates_to_query(self):
        """Execute calls query(); subclasses override query()."""
        class ConcreteQuery(Query):
            def validate(self, body):
                return {}
            def query(self, validated_input):
                return {"data": "ok"}

        q = ConcreteQuery()
        out = q.execute(q.validate({}))
        assert out == {"data": "ok"}


class TestArtGalleryListQuery:
    """Test ArtGalleryListQuery."""

    @patch("indexes.bucket")
    def test_handle_returns_data_and_next_token(self, mock_bucket):
        mock_bucket.search.return_value = Page(keys=[], next_token=None)
        query = ArtGalleryListQuery()
        result = query.handler(body={"limit": 10})
        assert "data" in result
        assert "next_token" in result
        assert isinstance(result["data"], list)


class TestListQuery:
    """Test ListQuery base validate."""

    def test_list_query_request_defaults(self):
        query = ArtGalleryListQuery()
        validated = query.validate({})
        assert "next_token" in validated
        assert "limit" in validated


class TestDetailsQuery:
    """Test DetailsQuery validate."""

    def test_details_query_validate_accepts_id(self):
        query = ArtGalleryDetailsQuery()
        validated = query.validate({"id": "gallery-123"})
        assert validated["id"] is not None
        assert str(validated["id"]) == "gallery-123"


class TestArtGalleryDetailsQuery:
    """Test ArtGalleryDetailsQuery execution with mocked repository."""

    @patch("queries.ArtGalleryRepository")
    def test_handler_returns_data_wrapper(self, mock_repo_cls):
        gallery = ArtGallery.unserialize({
            "id": "g1",
            "boundary": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "owner_job_id": "j1",
            "title": "Test",
        })
        mock_repo_cls.return_value.get.return_value = gallery
        query = ArtGalleryDetailsQuery()
        result = query.handler(body={"id": "g1"})
        assert "data" in result
        assert result["data"]["id"] == "g1"
        assert result["data"]["title"] == "Test"


class TestJobListQuery:
    """Test JobListQuery execution with mocked index."""

    @patch("queries.JobsPrivateIndex")
    def test_handler_returns_data_and_next_token(self, mock_index_cls):
        mock_index = MagicMock()
        mock_index.search.return_value = ([], None)
        mock_index_cls.return_value = mock_index
        user = User.test()
        query = JobListQuery(user=user)
        result = query.handler(body={"limit": 10})
        assert "data" in result
        assert "next_token" in result
        assert isinstance(result["data"], list)
        mock_index.search.assert_called_once()


class TestJobDetailsQuery:
    """Test JobDetailsQuery execution with mocked repository."""

    @patch("queries.JobsRepository")
    def test_handler_returns_data_wrapper(self, mock_repo_cls):
        from attributes import Identifier
        from enums import StepName
        from enums import Status

        job = Job(
            id=Identifier("j1"),
            status=Status.PENDING,
            step_name=StepName.ART_GALLERY,
            meta={},
            stdout={},
        )
        mock_repo_cls.return_value.get.return_value = job
        user = User.test()
        query = JobDetailsQuery(user=user)
        result = query.handler(body={"id": "j1"})
        assert "data" in result
        assert result["data"]["id"] == "j1"
