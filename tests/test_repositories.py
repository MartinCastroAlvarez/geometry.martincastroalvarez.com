"""Tests for repositories package."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import api  # noqa: F401

from attributes import Identifier
from attributes import Limit
from attributes import Offset

from data import Page
from exceptions import CorruptionError
from exceptions import RecordNotFoundError
from exceptions import UnauthorizedError
from exceptions import ValidationError
from models import ArtGallery
from models import Job
from models import User
from repositories import ArtGalleryRepository
from repositories import JobsRepository
from repositories import Results


class TestRepositories:
    """Test repository exports and base types."""

    def test_art_gallery_repository_exists(self):
        repo = ArtGalleryRepository()
        assert repo is not None

    def test_results_dataclass(self):
        r = Results(records=[], next_token=None)
        assert r.records == []
        assert r.next_token is None

    def test_results_serialize(self):
        r = Results(records=[User.test()], next_token=Offset("next"))
        d = r.serialize()
        assert "records" in d and len(d["records"]) == 1
        assert d["next_token"] == "next"

    def test_results_serialize_no_next_token(self):
        r = Results(records=[], next_token=None)
        d = r.serialize()
        assert d["records"] == []
        assert d["next_token"] == ""

    def test_art_gallery_repository_path(self):
        repo = ArtGalleryRepository()
        assert repo.path == "data/galleries"

    @patch("repositories.bucket")
    def test_art_gallery_repository_get_not_found_raises(self, mock_bucket):
        mock_bucket.load.return_value = None
        repo = ArtGalleryRepository()
        with pytest.raises(RecordNotFoundError, match="not found"):
            repo.get(Identifier("missing"))

    @patch("repositories.bucket")
    def test_art_gallery_repository_get_id_mismatch_raises(self, mock_bucket):
        mock_bucket.load.return_value = {"id": "other", "boundary": []}
        repo = ArtGalleryRepository()
        with pytest.raises(CorruptionError, match="ID mismatch"):
            repo.get(Identifier("g1"))

    @patch("repositories.bucket")
    def test_art_gallery_repository_save_and_get(self, mock_bucket):
        gallery_data = {
            "id": "g1",
            "boundary": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "obstacles": {},
            "created_at": "",
            "updated_at": "",
            "owner_email": "u@e.com",
            "owner_job_id": "job1",
            "title": "T",
        }
        mock_bucket.load.return_value = gallery_data
        repo = ArtGalleryRepository()
        gallery = ArtGallery.unserialize(gallery_data)
        saved = repo.save(gallery)
        assert saved is not None
        mock_bucket.save.assert_called()

    @patch("repositories.bucket")
    def test_art_gallery_repository_delete(self, mock_bucket):
        mock_bucket.delete.return_value = True
        repo = ArtGalleryRepository()
        repo.delete(Identifier("g1"))
        mock_bucket.delete.assert_called_once()

    @patch("repositories.bucket")
    def test_art_gallery_repository_exists(self, mock_bucket):
        mock_bucket.exists.return_value = True
        repo = ArtGalleryRepository()
        assert repo.exists(Identifier("g1")) is True

    @patch("repositories.bucket")
    def test_art_gallery_repository_search_empty(self, mock_bucket):
        mock_bucket.search.return_value = Page(keys=[], next_token=None)
        repo = ArtGalleryRepository()
        results = repo.search(limit=Limit(10))
        assert len(results.records) == 0
        assert results.next_token is None

    def test_jobs_repository_path_includes_slug(self):
        user = User.test()
        repo = JobsRepository(user=user)
        assert "jobs" in repo.path
        assert user.email.slug in repo.path

    def test_private_repository_not_authenticated_raises(self):
        anon = User.anonymous()
        with pytest.raises(UnauthorizedError, match="not authenticated"):
            _ = JobsRepository(user=anon).path

    @patch("repositories.bucket")
    def test_repository_save_wrong_model_raises(self, mock_bucket):
        repo = ArtGalleryRepository()
        with pytest.raises(ValidationError, match="must be"):
            repo.save(Job(id=Identifier("j1"), stdin={}))
