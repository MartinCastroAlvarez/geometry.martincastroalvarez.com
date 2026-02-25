"""Tests for interfaces package."""

from interfaces import Serializable


class TestSerializable:
    """Test Serializable base."""

    def test_serializable_is_abstract(self):
        # Serializable is ABC; subclasses implement serialize/unserialize
        assert hasattr(Serializable, "serialize")
        assert hasattr(Serializable, "unserialize")
