"""Tests for exceptions module."""

import http

import pytest
from exceptions import ConflictError
from exceptions import GeometryException
from exceptions import InvalidActionError
from exceptions import MethodNotAllowedError
from exceptions import NotFoundError
from exceptions import PathMissingResourceIdError
from exceptions import RecordNotFoundError
from exceptions import ServiceUnavailableError
from exceptions import UnauthorizedError
from exceptions import ValidationError


class TestGeometryException:
    """Test base GeometryException."""

    def test_code_default(self):
        e = GeometryException("msg")
        assert e.code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        assert e.message == "msg"

    def test_message_stored(self):
        e = GeometryException("custom message")
        assert str(e) == "custom message"
        assert e.message == "custom message"


class TestValidationError:
    """Test ValidationError."""

    def test_code_bad_request(self):
        e = ValidationError("invalid")
        assert e.code == http.HTTPStatus.BAD_REQUEST


class TestMethodNotAllowedError:
    """Test MethodNotAllowedError."""

    def test_code_method_not_allowed(self):
        e = MethodNotAllowedError()
        assert e.code == http.HTTPStatus.METHOD_NOT_ALLOWED


class TestPathMissingResourceIdError:
    """Test PathMissingResourceIdError."""

    def test_raises_with_message(self):
        with pytest.raises(PathMissingResourceIdError) as exc_info:
            raise PathMissingResourceIdError("Path must include resource id")
        assert "resource id" in str(exc_info.value).lower()


class TestNotFoundError:
    def test_code_not_found(self):
        e = NotFoundError("not found")
        assert e.code == http.HTTPStatus.NOT_FOUND


class TestUnauthorizedError:
    def test_code_unauthorized(self):
        e = UnauthorizedError("auth required")
        assert e.code == http.HTTPStatus.UNAUTHORIZED


class TestRecordNotFoundError:
    def test_code_not_found(self):
        e = RecordNotFoundError("record missing")
        assert e.code == http.HTTPStatus.NOT_FOUND


class TestConflictError:
    def test_code_conflict(self):
        e = ConflictError()
        assert e.code == http.HTTPStatus.CONFLICT


class TestInvalidActionError:
    def test_code_bad_request(self):
        e = InvalidActionError()
        assert e.code == http.HTTPStatus.BAD_REQUEST


class TestServiceUnavailableError:
    def test_code_service_unavailable(self):
        e = ServiceUnavailableError()
        assert e.code == http.HTTPStatus.SERVICE_UNAVAILABLE
