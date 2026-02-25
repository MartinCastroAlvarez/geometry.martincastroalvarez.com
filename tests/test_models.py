"""Tests for models package."""

from models import User


class TestUser:
    """Test User model."""

    def test_anonymous(self):
        u = User.anonymous()
        assert u is User.ANONYMOUS_USER
        assert not u.is_authenticated()

    def test_test_user(self):
        u = User.test()
        assert u.is_authenticated()
        assert str(u.email) == User.TEST_EMAIL
        assert u.name == User.TEST_NAME

    def test_serialize(self):
        u = User.test()
        d = u.serialize()
        assert "id" in d and "email" in d and "name" in d
        assert d["email"] == User.TEST_EMAIL

    def test_unserialize(self):
        u = User.unserialize({"email": "a@b.com", "name": "Ab"})
        assert str(u.email) == "a@b.com"
        assert u.name == "Ab"
