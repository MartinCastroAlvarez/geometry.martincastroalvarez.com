"""Tests for indexes package."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from attributes import Identifier
from attributes import Limit
from attributes import Offset
from data import Page
from exceptions import RecordNotFoundError
from exceptions import ValidationError
from indexes import ArtGalleryPublicIndex
from indexes import Indexed
from indexes import JobsPrivateIndex
from models import User

import api  # noqa: F401


class TestIndexed:
    """Test Indexed (index entry serialization)."""

    def test_serialize(self):
        entry = Indexed(index_id=Identifier("id1"), real_id=Identifier("r1"))
        d = entry.serialize()
        assert d["index_id"] == "id1" and d["real_id"] == "r1"

    def test_unserialize(self):
        entry = Indexed.unserialize({"index_id": "id1", "real_id": "r1"})
        assert str(entry.index_id) == "id1" and str(entry.real_id) == "r1"

    def test_unserialize_not_dict_raises(self):
        with pytest.raises(ValidationError, match="must be a dict"):
            Indexed.unserialize([])


class TestArtGalleryPublicIndex:
    """Test ArtGalleryPublicIndex."""

    def test_index_path(self):
        idx = ArtGalleryPublicIndex()
        assert idx.path == "index/galleries/"
        assert idx.NAME == "galleries"

    @patch("indexes.bucket")
    def test_get_not_found_raises(self, mock_bucket):
        mock_bucket.load.return_value = None
        idx = ArtGalleryPublicIndex()
        with pytest.raises(RecordNotFoundError, match="not found"):
            idx.get(Identifier("missing"))

    @patch("indexes.bucket")
    def test_get_returns_record(self, mock_bucket):
        mock_bucket.load.return_value = {"index_id": "123", "real_id": "g1"}
        idx = ArtGalleryPublicIndex()
        fake_repo = MagicMock()
        fake_repo.get.return_value = "gallery_record"
        idx.repository = fake_repo
        rec = idx.get(Identifier("123"))
        assert rec == "gallery_record"
        fake_repo.get.assert_called_once()

    @patch("indexes.bucket")
    def test_get_serialized(self, mock_bucket):
        mock_bucket.load.return_value = {"index_id": "123", "real_id": "g1"}
        fake_repo = MagicMock()
        fake_repo.get.return_value = MagicMock(serialize=lambda: {"id": "g1"})
        idx = ArtGalleryPublicIndex()
        idx.repository = fake_repo
        d = idx.get_serialized(Identifier("123"))
        assert d == {"id": "g1"}

    @patch("indexes.bucket")
    def test_save(self, mock_bucket):
        idx = ArtGalleryPublicIndex()
        entry = Indexed(index_id=Identifier("cid"), real_id=Identifier("g1"))
        idx.save(entry)
        mock_bucket.save.assert_called_once()
        call_args = mock_bucket.save.call_args[0]
        assert "cid.json" in call_args[0]
        assert call_args[1]["index_id"] == "cid"

    def test_save_non_indexed_raises(self):
        idx = ArtGalleryPublicIndex()
        with pytest.raises(ValidationError, match="must be Indexed"):
            idx.save({"index_id": "x", "real_id": "y"})

    @patch("indexes.bucket")
    def test_delete(self, mock_bucket):
        mock_bucket.delete.return_value = True
        idx = ArtGalleryPublicIndex()
        assert idx.delete(Identifier("cid")) is True
        mock_bucket.delete.assert_called_once()

    @patch("indexes.bucket")
    def test_exists(self, mock_bucket):
        mock_bucket.exists.return_value = True
        idx = ArtGalleryPublicIndex()
        assert idx.exists(Identifier("cid")) is True

    @patch("indexes.bucket")
    def test_search_empty_page(self, mock_bucket):
        mock_bucket.search.return_value = Page(keys=[], next_token=None)
        idx = ArtGalleryPublicIndex()
        records, token = idx.search(limit=Limit(10))
        assert records == []
        assert token is None

    @patch("indexes.bucket")
    def test_search_with_keys_loads_records(self, mock_bucket):
        mock_bucket.search.return_value = Page(
            keys=["index/galleries/k1.json"],
            next_token=Offset("next"),
        )
        mock_bucket.load.side_effect = [{"index_id": "k1", "real_id": "g1"}]
        fake_repo = MagicMock()
        fake_repo.get.return_value = MagicMock()
        idx = ArtGalleryPublicIndex()
        idx.repository = fake_repo
        records, token = idx.search(limit=Limit(10))
        assert len(records) == 1
        assert str(token) == "next"

    @patch("indexes.bucket")
    def test_search_stale_key_deleted_read_repair(self, mock_bucket):
        """When bucket.load returns None for a key, index deletes it (read-repair) and skips."""
        mock_bucket.search.return_value = Page(
            keys=["index/galleries/stale.json", "index/galleries/ok.json"],
            next_token=None,
        )
        mock_bucket.load.side_effect = [None, {"index_id": "ok", "real_id": "g1"}]
        fake_repo = MagicMock()
        fake_repo.get.return_value = MagicMock()
        idx = ArtGalleryPublicIndex()
        idx.repository = fake_repo
        records, token = idx.search(limit=Limit(10))
        assert len(records) == 1
        mock_bucket.delete.assert_called_once()
        assert "stale" in str(mock_bucket.delete.call_args[0][0])

    @patch("indexes.bucket")
    def test_all_iterates_with_read_repair(self, mock_bucket):
        """Index.all() yields records and skips stale keys (load returns None)."""
        mock_bucket.search.side_effect = [
            Page(keys=["index/galleries/a.json"], next_token=Offset("next")),
            Page(keys=[], next_token=None),
        ]
        mock_bucket.load.side_effect = [{"index_id": "a", "real_id": "g1"}]
        fake_repo = MagicMock()
        fake_repo.get.return_value = MagicMock()
        idx = ArtGalleryPublicIndex()
        idx.repository = fake_repo
        out = list(idx.all())
        assert len(out) == 1
        assert mock_bucket.search.call_count >= 1

    @patch("indexes.bucket")
    def test_all_stale_key_deleted(self, mock_bucket):
        """Index.all() deletes key when load returns None."""
        mock_bucket.search.return_value = Page(keys=["index/galleries/stale.json"], next_token=None)
        mock_bucket.load.return_value = None
        idx = ArtGalleryPublicIndex()
        idx.repository = MagicMock()
        out = list(idx.all())
        assert len(out) == 0
        mock_bucket.delete.assert_called_once()


class TestJobsPrivateIndex:
    """Test JobsPrivateIndex (user-scoped path)."""

    def test_path_includes_user_slug(self):
        user = User.test()
        idx = JobsPrivateIndex(user_email=user.email)
        assert "jobs" in idx.path
        assert user.email.slug in idx.path
