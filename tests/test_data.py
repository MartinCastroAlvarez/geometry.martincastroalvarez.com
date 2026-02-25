"""Tests for data package."""

import pytest

from attributes import Offset

from data import Page


class TestPage:
    """Test Page (search results with pagination)."""

    def test_empty_page(self):
        p = Page()
        assert list(p) == []
        assert p.continues is False
        assert len(p) == 0

    def test_page_with_keys(self):
        p = Page(keys=["a", "b"], next_token=None)
        assert list(p) == ["a", "b"]
        assert p.continues is False

    def test_page_continues(self):
        p = Page(keys=[], next_token=Offset("token"))
        assert p.continues is True


class TestOffset:
    """Test Offset attribute."""

    def test_valid(self):
        assert Offset("abc") == "abc"

    def test_none_raises(self):
        from exceptions import ValidationError

        with pytest.raises(ValidationError):
            Offset(None)

    def test_empty_raises(self):
        from exceptions import ValidationError

        with pytest.raises(ValidationError):
            Offset("   ")
