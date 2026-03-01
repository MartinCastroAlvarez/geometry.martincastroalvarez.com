"""Tests for mutations package."""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from attributes import Email
from attributes import Identifier
from exceptions import JobStdoutMissingGeometryError
from exceptions import UnauthorizedError
from exceptions import ValidationError
from models import User
from mutations import ArtGalleryPublishMutation
from mutations import JobMutation
from mutations import JobUpdateMutation
from mutations import Mutation
from mutations import MutationResponse
from mutations import gallery_id_from_job_and_user

import api  # noqa: F401


class TestMutationBase:
    """Test Mutation base."""

    def test_mutation_response_typed_dict(self):
        r: MutationResponse = {"ok": True}
        assert r["ok"] is True


class TestGalleryIdFromJobAndUser:
    """Test gallery_id_from_job_and_user."""

    def test_returns_identifier(self):
        gid = gallery_id_from_job_and_user(Identifier("j1"), Email("u@e.com"))
        assert gid is not None
        assert len(str(gid)) > 0


class TestJobMutation:
    """Test JobMutation validate and execute."""

    def test_validate_missing_boundary_raises(self):
        user = User.test()
        handler = JobMutation(user=user)
        with pytest.raises(ValidationError, match="boundary"):
            handler.validate({})

    def test_validate_boundary_not_list_raises(self):
        user = User.test()
        handler = JobMutation(user=user)
        with pytest.raises(ValidationError, match="list"):
            handler.validate({"boundary": "not a list"})

    def test_validate_obstacles_not_list_raises(self):
        user = User.test()
        handler = JobMutation(user=user)
        with pytest.raises(ValidationError, match="list"):
            handler.validate({"boundary": [[0, 0], [1, 0], [0, 1]], "obstacles": "x"})

    def test_validate_success(self):
        user = User.test()
        handler = JobMutation(user=user)
        req = handler.validate({"boundary": [[0, 0], [2, 0], [1, 2]], "obstacles": []})
        assert req["boundary"] is not None
        assert len(req["obstacles"]) == 0

    @patch("mutations.queue")
    @patch("mutations.JobsRepository")
    @patch("mutations.JobsPrivateIndex")
    @patch("mutations.Countdown")
    def test_execute_creates_job(self, mock_countdown_cls, mock_index_cls, mock_repo_cls, mock_queue):
        user = User.test()
        mock_repo = MagicMock()
        mock_repo_cls.return_value = mock_repo
        mock_index = MagicMock()
        mock_index_cls.return_value = mock_index
        mock_countdown_cls.from_timestamp.return_value = "countdown-123"
        handler = JobMutation(user=user)
        from geometry import Polygon
        from structs import Table

        boundary = Polygon.unserialize([[0, 0], [2, 0], [1, 2]])
        obstacles = Table.unserialize([])
        req = {"boundary": boundary, "obstacles": obstacles}
        result = handler.execute(req)
        assert "id" in result
        mock_repo.save.assert_called_once()
        mock_queue.put.assert_called_once()


class TestJobUpdateMutation:
    """Test JobUpdateMutation validate and execute."""

    def test_validate_missing_meta_raises(self):
        user = User.test()
        handler = JobUpdateMutation(user=user)
        with pytest.raises(ValidationError, match="meta"):
            handler.validate({"id": "j1"})

    def test_validate_meta_not_dict_raises(self):
        user = User.test()
        handler = JobUpdateMutation(user=user)
        with pytest.raises(ValidationError, match="meta must be a dict"):
            handler.validate({"id": "j1", "meta": []})

    def test_validate_meta_keys_non_string_raises(self):
        user = User.test()
        handler = JobUpdateMutation(user=user)
        with pytest.raises(ValidationError, match="meta keys"):
            handler.validate({"id": "j1", "meta": {123: "v"}})

    def test_validate_meta_values_non_string_raises(self):
        user = User.test()
        handler = JobUpdateMutation(user=user)
        with pytest.raises(ValidationError, match="meta values"):
            handler.validate({"id": "j1", "meta": {"k": 123}})

    def test_validate_success(self):
        user = User.test()
        handler = JobUpdateMutation(user=user)
        req = handler.validate({"id": "j1", "meta": {"title": "My Gallery"}})
        assert str(req["job_id"]) == "j1"
        assert req["meta"]["title"] == "My Gallery"

    def test_validate_success_meta_value_none_becomes_empty_string(self):
        user = User.test()
        handler = JobUpdateMutation(user=user)
        req = handler.validate({"id": "j1", "meta": {"title": "T", "subtitle": None}})
        assert req["meta"]["title"] == "T"
        assert req["meta"]["subtitle"] == ""

    @patch("mutations.ArtGalleryRepository")
    @patch("mutations.JobsRepository")
    def test_execute_updates_job_no_title(self, mock_job_repo_cls, mock_gallery_repo_cls):
        user = User.test()
        mock_job_repo = MagicMock()
        mock_job_repo_cls.return_value = mock_job_repo
        job = MagicMock()
        job.id = Identifier("j1")
        job.meta = {}
        mock_job_repo.get.return_value = job
        handler = JobUpdateMutation(user=user)
        result = handler.execute({"job_id": Identifier("j1"), "meta": {"k": "v"}})
        assert result is not None
        mock_job_repo.save.assert_called_once()
        mock_gallery_repo_cls.return_value.exists.assert_not_called()

    @patch("mutations.ArtGalleryPublicIndex")
    @patch("mutations.ArtGalleryRepository")
    @patch("mutations.JobsRepository")
    @patch("mutations.Countdown")
    def test_execute_updates_job_and_gallery_title(
        self, mock_countdown_cls, mock_job_repo_cls, mock_gallery_repo_cls, mock_index_cls
    ):
        user = User.test()
        mock_job_repo = MagicMock()
        mock_job_repo_cls.return_value = mock_job_repo
        job = MagicMock()
        job.id = Identifier("j1")
        job.meta = {}
        job.is_finished.return_value = True
        job.stdout = {
            "boundary": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "obstacles": {},
            "guards": {},
        }
        job.created_at = "2024-01-01T12:00:00"
        job.updated_at = "2024-01-01T12:00:00"
        mock_job_repo.get.return_value = job
        mock_countdown_cls.from_timestamp.return_value = "20240101120000"
        mock_gallery_repo = MagicMock()
        mock_gallery_repo_cls.return_value = mock_gallery_repo
        mock_gallery_repo.exists.return_value = True
        mock_index = MagicMock()
        mock_index_cls.return_value = mock_index
        handler = JobUpdateMutation(user=user)
        result = handler.execute({"job_id": Identifier("j1"), "meta": {"title": "New Title"}})
        assert result is not None
        mock_gallery_repo.save.assert_called_once()


class TestArtGalleryPublishMutation:
    """Test ArtGalleryPublishMutation validate and execute."""

    def test_validate_success(self):
        user = User.test()
        handler = ArtGalleryPublishMutation(user=user)
        req = handler.validate({"id": "job-123"})
        assert str(req["job_id"]) == "job-123"

    @patch("mutations.ArtGalleryPublicIndex")
    @patch("mutations.ArtGalleryRepository")
    @patch("mutations.JobsRepository")
    @patch("mutations.Countdown")
    def test_execute_publishes_gallery(self, mock_countdown_cls, mock_job_repo_cls, mock_gallery_repo_cls, mock_index_cls):
        user = User.test()
        mock_job_repo = MagicMock()
        mock_job_repo_cls.return_value = mock_job_repo
        job = MagicMock()
        job.id = Identifier("j1")
        job.is_finished.return_value = True
        job.stdout = {
            "boundary": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "obstacles": {},
            "guards": {},
        }
        job.meta = {"title": "My Gallery"}
        job.created_at = "2024-01-01T12:00:00"
        job.updated_at = "2024-01-01T12:00:00"
        mock_job_repo.get.return_value = job
        mock_countdown_cls.from_timestamp.return_value = "20240101120000"
        mock_gallery_repo = MagicMock()
        mock_gallery_repo_cls.return_value = mock_gallery_repo
        mock_index = MagicMock()
        mock_index_cls.return_value = mock_index
        handler = ArtGalleryPublishMutation(user=user)
        result = handler.execute({"job_id": Identifier("j1")})
        assert "id" in result
        mock_gallery_repo.save.assert_called_once()
        mock_index.index.assert_called_once()

    @patch("mutations.JobsRepository")
    def test_execute_job_not_finished_raises(self, mock_job_repo_cls):
        user = User.test()
        mock_job_repo = MagicMock()
        mock_job_repo_cls.return_value = mock_job_repo
        job = MagicMock()
        job.is_finished.return_value = False
        mock_job_repo.get.return_value = job
        handler = ArtGalleryPublishMutation(user=user)
        with pytest.raises(ValidationError, match="Job must be successfully finished"):
            handler.execute({"job_id": Identifier("j1")})

    @patch("mutations.JobsRepository")
    def test_execute_stdout_empty_boundary_raises(self, mock_job_repo_cls):
        user = User.test()
        mock_job_repo = MagicMock()
        mock_job_repo_cls.return_value = mock_job_repo
        job = MagicMock()
        job.id = Identifier("j1")
        job.is_finished.return_value = True
        job.stdout = {"boundary": [], "obstacles": {}}
        job.meta = {}
        job.created_at = "2024-01-01T12:00:00"
        job.updated_at = "2024-01-01T12:00:00"
        mock_job_repo.get.return_value = job
        handler = ArtGalleryPublishMutation(user=user)
        with pytest.raises(JobStdoutMissingGeometryError, match="no boundary or obstacles"):
            handler.execute({"job_id": Identifier("j1")})
