"""Tests for repositories package."""

from attributes import Offset

from models import User
from repositories import ArtGalleryRepository
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
