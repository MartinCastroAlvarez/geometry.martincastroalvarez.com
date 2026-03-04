"""Tests for models package."""

from attributes import Identifier
from geometry import ConvexComponent
from geometry import Point
from models import ArtGallery
from models import User
from settings import ANONYMOUS_EMAIL
from settings import ANONYMOUS_NAME
from settings import TEST_EMAIL
from settings import TEST_NAME


class TestUser:
    """Test User model."""

    def test_anonymous(self):
        u = User.anonymous()
        assert not u.is_authenticated()
        assert str(u.email) == ANONYMOUS_EMAIL
        assert u.name == ANONYMOUS_NAME

    def test_test_user(self):
        u = User.test()
        assert u.is_authenticated()
        assert str(u.email) == TEST_EMAIL
        assert u.name == TEST_NAME

    def test_serialize(self):
        u = User.test()
        d = u.serialize()
        assert "id" in d and "email" in d and "name" in d
        assert d["email"] == TEST_EMAIL

    def test_unserialize(self):
        u = User.unserialize({"email": "a@b.com", "name": "Ab"})
        assert str(u.email) == "a@b.com"
        assert u.name == "Ab"


class TestArtGalleryAdjacency:
    """Test ArtGallery adjacency field (serialize/unserialize)."""

    def test_unserialize_with_adjacency(self):
        c = ConvexComponent([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        h = hash(c)
        data = {
            "id": "g1",
            "boundary": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "owner_job_id": "j1",
            "title": "Test",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "obstacles": {},
            "ears": {},
            "convex_components": {str(h): c.serialize()},
            "adjacency": {str(h): [999]},
            "guards": {},
            "visibility": {},
            "stitched": [],
            "stitches": [],
            "coverage": [[0, 0], [1, 0], [0.5, 0.5]],
        }
        gallery = ArtGallery.unserialize(data)
        assert len(gallery.adjacency) == 1
        adj = list(gallery.adjacency)[0]
        assert Identifier(999) in adj.items
        assert len(gallery.coverage) == 3

    def test_serialize_includes_adjacency(self):
        data = {
            "id": "g1",
            "boundary": [[0, 0], [1, 0], [1, 1], [0, 1]],
            "owner_job_id": "j1",
            "title": "Test",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "obstacles": {},
            "ears": {},
            "convex_components": {},
            "guards": {},
            "visibility": {},
            "stitched": [],
            "stitches": [],
        }
        gallery = ArtGallery.unserialize(data)
        out = gallery.serialize()
        assert "adjacency" in out
        assert isinstance(out["adjacency"], dict)
        assert "coverage" in out
        assert isinstance(out["coverage"], list)
        assert len(gallery.coverage) == 0
        assert out["coverage"] == []
