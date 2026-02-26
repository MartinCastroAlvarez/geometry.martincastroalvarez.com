"""Tests for queries package."""

from unittest.mock import patch

from data import Page
from queries import ArtGalleryListQuery
from queries.base import ListQuery


class TestArtGalleryListQuery:
    """Test ArtGalleryListQuery."""

    @patch("indexes.base.bucket")
    def test_handle_returns_records_and_next_token(self, mock_bucket):
        mock_bucket.search.return_value = Page(keys=[], next_token=None)
        query = ArtGalleryListQuery()
        result = query.handle(body={"limit": 10})
        assert "records" in result
        assert "next_token" in result
        assert isinstance(result["records"], list)


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
        from queries.galleries import ArtGalleryDetailsQuery

        query = ArtGalleryDetailsQuery()
        validated = query.validate({"id": "gallery-123"})
        assert validated["id"] is not None
        assert str(validated["id"]) == "gallery-123"
