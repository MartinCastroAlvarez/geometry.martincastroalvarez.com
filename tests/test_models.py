"""Tests for models package."""

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
