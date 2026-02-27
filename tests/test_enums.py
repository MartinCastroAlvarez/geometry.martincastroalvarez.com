"""Tests for enums package."""

import pytest

from enums import Action
from enums import Method
from enums import Status
from exceptions import InvalidActionError
from exceptions import MethodNotAllowedError
from exceptions import ValidationError


class TestMethod:
    """Test Method enum."""

    def test_parse_get(self):
        assert Method.parse("GET") == Method.GET
        assert Method.parse("get") == Method.GET

    def test_parse_post(self):
        assert Method.parse("POST") == Method.POST

    def test_parse_options(self):
        assert Method.parse("OPTIONS") == Method.OPTIONS

    def test_parse_none_raises(self):
        with pytest.raises(MethodNotAllowedError):
            Method.parse(None)

    def test_parse_invalid_raises(self):
        with pytest.raises(MethodNotAllowedError):
            Method.parse("PUT")


class TestStatus:
    """Test Status enum."""

    def test_parse_success(self):
        assert Status.parse("success") == Status.SUCCESS
        assert Status.parse("FAILED") == Status.FAILED
        assert Status.parse("pending") == Status.PENDING

    def test_parse_none_raises(self):
        with pytest.raises(ValidationError):
            Status.parse(None)

    def test_parse_invalid_raises(self):
        with pytest.raises(ValidationError):
            Status.parse("invalid")


class TestAction:
    """Test Action enum."""

    def test_parse_default_start(self):
        assert Action.parse(None) == Action.START
        assert Action.parse("") == Action.START

    def test_parse_report(self):
        assert Action.parse("report") == Action.REPORT

    def test_parse_invalid_raises(self):
        with pytest.raises(InvalidActionError):
            Action.parse("invalid")
