"""
Custom exceptions for the geometry (art gallery) API.

Title
-----
Geometry API Exceptions

Context
-------
All exceptions inherit from GeometryException and set a `code` attribute
(http.HTTPStatus) used for HTTP status codes. The interceptor catches
GeometryException and generic Exception, then builds a JSON error response
via ApiResponse.unserialize(exception). This keeps error handling consistent
across API Gateway and allows clients to rely on error.code and error.type.
ValidationError (400), NotFoundError/RecordNotFoundError (404), UnauthorizedError
(401), ForbiddenError (403), and others cover typical API and storage failures.
StorageError is for invalid S3 data; ValidationError is for bad request input.

Examples:
    raise ValidationError("id is required")
    raise RecordNotFoundError("Job xyz not found")
    try:
        ...
    except GeometryException as e:
        print(e.code.value, str(e))
    response = ApiResponse.unserialize(e)
"""

import http


class GeometryException(Exception):
    """
    Base exception for geometry API errors.

    For example, to check the HTTP code:
    >>> e = ValidationError("bad input")
    >>> e.code
    <HTTPStatus.BAD_REQUEST: 400>
    """

    code: http.HTTPStatus = http.HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message)
        self.message = message


class ValidationError(GeometryException):
    """
    Raised when input validation fails.
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


class NotFoundError(GeometryException):
    """
    Raised when a requested resource is not found.
    """

    code: http.HTTPStatus = http.HTTPStatus.NOT_FOUND

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class UnauthorizedError(GeometryException):
    """
    Raised when authentication is required but missing or invalid.
    """

    code: http.HTTPStatus = http.HTTPStatus.UNAUTHORIZED

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message)


class ForbiddenError(GeometryException):
    """
    Raised when access is forbidden for authenticated users.
    """

    code: http.HTTPStatus = http.HTTPStatus.FORBIDDEN

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message)


class ConflictError(GeometryException):
    """
    Raised when a request conflicts with the current state.
    """

    code: http.HTTPStatus = http.HTTPStatus.CONFLICT

    def __init__(self, message: str = "Request conflicts with current state"):
        super().__init__(message)


class ServiceUnavailableError(GeometryException):
    """
    Raised when external services are unavailable.
    """

    code: http.HTTPStatus = http.HTTPStatus.SERVICE_UNAVAILABLE

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message)


class ConfigurationError(GeometryException):
    """
    Raised when there are configuration issues.
    """

    code: http.HTTPStatus = http.HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "Configuration error"):
        super().__init__(message)


class StorageError(GeometryException):
    """
    Raised when stored data or storage response is invalid (not a user input error).
    Use for corrupt/invalid S3 response shape or object content; use ValidationError for bad request input.
    """

    code: http.HTTPStatus = http.HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "Invalid stored data or storage response"):
        super().__init__(message)


class MethodNotAllowedError(GeometryException):
    """
    Raised when a request method is not allowed.
    """

    code: http.HTTPStatus = http.HTTPStatus.METHOD_NOT_ALLOWED

    def __init__(self, message: str = "Method not allowed"):
        super().__init__(message)


class RecordNotFoundError(GeometryException):
    """
    Raised when a record is not found.
    """

    code: http.HTTPStatus = http.HTTPStatus.NOT_FOUND

    def __init__(self, message: str = "Record not found"):
        super().__init__(message)


class CorruptionError(GeometryException):
    """
    Raised when a record is corrupted.
    """

    code: http.HTTPStatus = http.HTTPStatus.CONFLICT

    def __init__(self, message: str = "Record corrupted"):
        super().__init__(message)


class InvalidActionError(GeometryException):
    """
    Raised when worker action is not 'run' or 'report'.
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Action must be 'run' or 'report'"):
        super().__init__(message)


class BoxInvalidEdgeError(GeometryException):
    """
    Raised when a box has invalid edges (e.g. non-vertical or non-horizontal).
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Box has invalid edge"):
        super().__init__(message)


class SerializedInvalidDictError(GeometryException):
    """
    Raised when unserializing from an invalid dict (e.g. missing keys or wrong type).
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Invalid dict for unserialize"):
        super().__init__(message)


class SequenceMultipleOverlapsError(GeometryException):
    """
    Raised when Sequence.__and__ finds multiple disjoint overlapping regions.
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Sequences overlap in multiple places"):
        super().__init__(message)


class PathMissingResourceIdError(GeometryException):
    """
    Raised when path has no resource id (e.g. v1/galleries instead of v1/galleries/:id).
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Path must include resource id (e.g. v1/galleries/:id)"):
        super().__init__(message)
