"""Tests for api.api: ApiRequest, ApiResponse, Path, handler."""

import http
import json
from unittest.mock import patch

import pytest

from api.api import ApiRequest
from api.api import ApiResponse
from api.api import handler
from api.api import ROUTES
from attributes import Identifier
from attributes import Origin
from attributes import Path
from data import Page
from enums import Stage
from enums import Status
from exceptions import PathMissingResourceIdError
from exceptions import ValidationError
from models import Job
from models import User


class TestApiRequest:
    """Test cases for ApiRequest."""

    def test_init_minimal(self):
        event = {}
        request = ApiRequest(event)
        assert request.path == Path("")
        assert request.http_method == ""
        assert request.headers == {}
        assert request.query_params == {}
        assert request.path_params == {}
        assert request._body == ""
        assert not request.is_base64_encoded
        assert isinstance(request.user, User)

    def test_init_full_event(self):
        event = {
            "path": "/v1/galleries",
            "httpMethod": "GET",
            "headers": {"Content-Type": "application/json"},
            "queryStringParameters": {"limit": "10"},
            "pathParameters": {"id": "123"},
            "body": '{"name": "test"}',
            "isBase64Encoded": True,
        }
        request = ApiRequest(event)
        assert request.path == Path("v1/galleries")
        assert request.http_method == "GET"
        assert request.query_params == {"limit": "10"}
        assert request.path_params == {"id": "123"}
        assert request._body == '{"name": "test"}'
        assert request.is_base64_encoded

    def test_unserialize_classmethod(self):
        event = {"path": "/v1/jobs", "httpMethod": "POST"}
        request = ApiRequest.unserialize(event)
        assert isinstance(request, ApiRequest)
        assert request.path == Path("v1/jobs")
        assert request.http_method == "POST"

    def test_body_empty(self):
        request = ApiRequest({"body": ""})
        assert request.body == {}

    def test_body_valid_json(self):
        request = ApiRequest({"body": '{"a": 1, "b": 2}'})
        assert request.body == {"a": 1, "b": 2}

    def test_body_invalid_json(self):
        request = ApiRequest({"body": "{ invalid }"})
        assert request.body == {}

    def test_body_none(self):
        request = ApiRequest({"body": None})
        assert request.body == {}

    def test_serialize_raises(self):
        request = ApiRequest({})
        with pytest.raises(NotImplementedError):
            request.serialize()


class TestApiResponse:
    """Test cases for ApiResponse."""

    def test_init_minimal(self):
        r = ApiResponse(http.HTTPStatus.OK, '{"ok": true}', Origin(""))
        assert r.status_code == http.HTTPStatus.OK
        assert r.body == '{"ok": true}'
        assert r.headers == {}

    def test_to_dict(self):
        r = ApiResponse(http.HTTPStatus.CREATED, '{"created": true}', Origin(""))
        d = r.serialize()
        assert d["statusCode"] == 201
        assert d["body"] == '{"created": true}'
        assert "Content-Type" in d["headers"]
        assert "Access-Control-Allow-Origin" in d["headers"]

    def test_to_dict_localhost_origin(self):
        r = ApiResponse(http.HTTPStatus.OK, '{}', Origin("http://localhost:5173"))
        d = r.serialize()
        assert d["headers"]["Access-Control-Allow-Origin"] == "http://localhost:5173"

    def test_to_dict_subdomain_origin(self):
        r = ApiResponse(http.HTTPStatus.OK, '{}', Origin("https://geometry.martincastroalvarez.com"))
        d = r.serialize()
        assert d["headers"]["Access-Control-Allow-Origin"] == "https://geometry.martincastroalvarez.com"

    def test_from_error_validation_error(self):
        e = ValidationError("Invalid input")
        r = ApiResponse.unserialize(e)
        assert r.status_code == http.HTTPStatus.BAD_REQUEST
        body = json.loads(r.body)
        assert body["error"]["code"] == 400
        assert body["error"]["type"] == "ValidationError"
        assert body["error"]["message"] == "Invalid input"

    def test_from_error_generic_exception(self):
        e = Exception("Something went wrong")
        r = ApiResponse.unserialize(e)
        assert r.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
        body = json.loads(r.body)
        assert body["error"]["message"] == "Something went wrong"

    def test_to_dict_invalid_origin_uses_default(self):
        r = ApiResponse(http.HTTPStatus.OK, '{}', Origin("https://other.com"))
        d = r.serialize()
        assert d["headers"]["Access-Control-Allow-Origin"] == "https://geometry.martincastroalvarez.com"

    def test_to_dict_star_when_none(self):
        r = ApiResponse(http.HTTPStatus.OK, '{}', Origin(None))
        d = r.serialize()
        assert d["headers"]["Access-Control-Allow-Origin"] == "*"

    def test_serialize_returns_to_dict(self):
        r = ApiResponse(http.HTTPStatus.OK, '{}', Origin(""))
        d = r.serialize()
        assert d["statusCode"] == 200

    def test_unserialize_from_exception(self):
        r = ApiResponse.unserialize(ValidationError("bad input"))
        assert r.status_code == http.HTTPStatus.BAD_REQUEST
        assert "bad input" in r.body

    def test_unserialize_dict_raises_not_implemented(self):
        data = {"statusCode": 201, "body": "{}", "headers": {"Access-Control-Allow-Origin": "https://geometry.martincastroalvarez.com"}}
        with pytest.raises(NotImplementedError, match="does not support dict"):
            ApiResponse.unserialize(data)

    def test_unserialize_non_dict_non_exception_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            ApiResponse.unserialize("invalid")


class TestPath:
    """Test Path (attributes.Path) used by ApiRequest."""

    def test_path_normalized_no_leading_slash(self):
        p = Path("/v1/galleries")
        assert p == "v1/galleries"
        assert p.parts == ["v1", "galleries"]
        assert p.version == "v1"
        assert p.resource == "galleries"

    def test_path_id_raises_when_missing(self):
        p = Path("v1/galleries")
        with pytest.raises(PathMissingResourceIdError):
            _ = p.id

    def test_path_id_present(self):
        p = Path("v1/galleries/abc-123")
        assert p.id == "abc-123"


class TestHandler:
    """Test handler routing (without full Lambda event)."""

    @patch("indexes.bucket")
    @patch("api.api.Secret")
    def test_handler_returns_dict_for_list_galleries(self, mock_secret, mock_bucket):
        mock_secret.get.side_effect = lambda key: "test-secret" if key == "JWT_SECRET" else "test-token"
        mock_bucket.search.return_value = Page(keys=[], next_token=None)
        event = {
            "path": "/v1/galleries",
            "httpMethod": "GET",
            "headers": {"X-Auth": "test-token"},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = handler(event, None)
        assert isinstance(result, dict)
        assert "statusCode" in result
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "data" in body and "next_token" in body

    @patch("api.api.Secret")
    def test_handler_method_not_allowed(self, mock_secret):
        mock_secret.get.side_effect = lambda key: "test-secret" if key == "JWT_SECRET" else "test-token"
        event = {
            "path": "/v1/galleries",
            "httpMethod": "DELETE",
            "headers": {"X-Auth": "test-token"},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = handler(event, None)
        assert isinstance(result, dict)
        assert result["statusCode"] == 405
        body = json.loads(result["body"])
        assert "error" in body and body["error"]["type"] == "MethodNotAllowedError"

    def test_handler_options_returns_empty_dict(self):
        event = {
            "path": "/v1/galleries",
            "httpMethod": "OPTIONS",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = handler(event, None)
        assert isinstance(result, dict)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body == {}

    @patch("api.api.Secret")
    def test_handler_validation_error_returns_400(self, mock_secret):
        mock_secret.get.side_effect = lambda key: "test-secret" if key == "JWT_SECRET" else "test-token"
        event = {
            "path": "/v1/jobs",
            "httpMethod": "POST",
            "headers": {"X-Auth": "test-token"},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": "{}",
        }
        result = handler(event, None)
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"]["type"] == "ValidationError"

    @patch("api.api.Secret")
    def test_handler_auth_missing_token_returns_401(self, mock_secret):
        mock_secret.get.side_effect = lambda key: "test-secret" if key == "JWT_SECRET" else "test-token"
        event = {
            "path": "/v1/galleries",
            "httpMethod": "GET",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = handler(event, None)
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert "Unauthorized" in body["error"]["type"] or "401" in str(body["error"])

    @patch("api.api.jwt")
    @patch("api.api.Secret")
    def test_handler_auth_expired_token_returns_401(self, mock_secret, mock_jwt):
        ExpiredSignatureError = type("ExpiredSignatureError", (Exception,), {})
        mock_jwt.ExpiredSignatureError = ExpiredSignatureError
        mock_jwt.InvalidTokenError = type("InvalidTokenError", (Exception,), {})
        mock_secret.get.side_effect = lambda key: "secret" if key == "JWT_SECRET" else "test-token"
        mock_jwt.decode.side_effect = ExpiredSignatureError("expired")
        event = {
            "path": "/v1/galleries",
            "httpMethod": "GET",
            "headers": {"X-Auth": "bearer-expired-token"},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = handler(event, None)
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert "expired" in body["error"]["message"].lower() or "401" in str(body["error"])

    @patch("api.api.jwt")
    @patch("api.api.Secret")
    def test_handler_auth_invalid_token_returns_401(self, mock_secret, mock_jwt):
        InvalidTokenError = type("InvalidTokenError", (Exception,), {})
        mock_jwt.ExpiredSignatureError = type("ExpiredSignatureError", (Exception,), {})
        mock_jwt.InvalidTokenError = InvalidTokenError
        mock_secret.get.side_effect = lambda key: "secret" if key == "JWT_SECRET" else "test-token"
        mock_jwt.decode.side_effect = InvalidTokenError("invalid")
        event = {
            "path": "/v1/galleries",
            "httpMethod": "GET",
            "headers": {"X-Auth": "bearer-bad-token"},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = handler(event, None)
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert "invalid" in body["error"]["message"].lower() or "401" in str(body["error"])

    @patch("api.api.jwt")
    @patch("api.api.Secret")
    def test_handler_auth_missing_email_returns_401(self, mock_secret, mock_jwt):
        mock_secret.get.side_effect = lambda key: "secret" if key == "JWT_SECRET" else "test-token"
        mock_jwt.decode.return_value = {"name": "User"}
        mock_jwt.ExpiredSignatureError = type("ExpiredSignatureError", (Exception,), {})
        mock_jwt.InvalidTokenError = type("InvalidTokenError", (Exception,), {})
        event = {
            "path": "/v1/galleries",
            "httpMethod": "GET",
            "headers": {"X-Auth": "bearer-some-token"},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = handler(event, None)
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert "email" in body["error"]["message"].lower() or "401" in str(body["error"])

    @patch("queries.JobsRepository")
    @patch("api.api.Secret")
    def test_handler_path_id_extracted_from_path_for_job_details(self, mock_secret, mock_repo_cls):
        mock_secret.get.side_effect = lambda key: "test-secret" if key == "JWT_SECRET" else "test-token"
        mock_repo = mock_repo_cls.return_value
        mock_repo.get.return_value = Job(
            id=Identifier("j1"),
            status=Status.PENDING,
            stage=Stage.ART_GALLERY,
            meta={},
            stdout={},
        )
        event = {
            "path": "/v1/jobs/j1",
            "httpMethod": "GET",
            "headers": {"X-Auth": "test-token"},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = handler(event, None)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "data" in body and body["data"]["id"] == "j1"

    @patch("indexes.bucket")
    @patch("api.api.jwt")
    @patch("api.api.Secret")
    def test_handler_jwt_with_email_sets_user(self, mock_secret, mock_jwt, mock_bucket):
        """When JWT decode returns email, request.user is set (covers User construction in private wrapper)."""
        mock_secret.get.side_effect = lambda key: "secret" if key == "JWT_SECRET" else "test-token"
        mock_jwt.decode.return_value = {"email": "user@example.com", "name": "User", "avatarUrl": None}
        mock_jwt.ExpiredSignatureError = type("ExpiredSignatureError", (Exception,), {})
        mock_jwt.InvalidTokenError = type("InvalidTokenError", (Exception,), {})
        mock_bucket.search.return_value = Page(keys=[], next_token=None)
        event = {
            "path": "/v1/galleries",
            "httpMethod": "GET",
            "headers": {"X-Auth": "Bearer real-jwt-token"},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = handler(event, None)
        assert result["statusCode"] == 200


class TestInterceptor:
    """Test interceptor decorator: handler returning non-dict and generic exception path."""

    def test_interceptor_returns_500_when_handler_returns_non_dict(self):
        from api.api import interceptor

        @interceptor
        def fake_handler(request, context):
            return 123

        event = {
            "path": "/v1/galleries",
            "httpMethod": "GET",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = fake_handler(event, None)
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "error" in body and "Handler must return a dict" in body["error"]["message"]

    def test_interceptor_returns_error_response_on_generic_exception(self):
        from api.api import interceptor

        @interceptor
        def failing_handler(request, context):
            raise RuntimeError("something broke")

        event = {
            "path": "/v1/galleries",
            "httpMethod": "GET",
            "headers": {},
            "queryStringParameters": None,
            "pathParameters": None,
            "body": None,
        }
        result = failing_handler(event, None)
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["error"]["type"] == "RuntimeError"
        assert "something broke" in body["error"]["message"]


class TestROUTES:
    """Test ROUTES mapping."""

    def test_routes_has_galleries_and_jobs(self):
        assert Path("v1/galleries") in ROUTES or any("galleries" in str(k) for k in ROUTES)
        assert Path("v1/jobs") in ROUTES or any("jobs" in str(k) for k in ROUTES)
