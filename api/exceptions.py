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

For example, to raise and catch exceptions:
>>> raise ValidationError("id is required")
>>> raise RecordNotFoundError("Job xyz not found")
>>> try:
...     some_operation()
... except GeometryException as e:
...     e.code.value
400
>>> response = ApiResponse.unserialize(e)
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

    For example, to raise on invalid input:
    >>> raise ValidationError("id is required")
    For example, to catch from attribute validation:
    >>> try:
    ...     Email("")
    ... except ValidationError as e:
    ...     e.code
    400
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


class NotFoundError(GeometryException):
    """
    Raised when a requested resource is not found.

    For example, to raise when a secret is missing:
    >>> raise NotFoundError("Secret 'JWT_SECRET' not found")
    """

    code: http.HTTPStatus = http.HTTPStatus.NOT_FOUND

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class UnauthorizedError(GeometryException):
    """
    Raised when authentication is required but missing or invalid.

    For example, to raise when user is not authenticated:
    >>> raise UnauthorizedError("User must be authenticated")
    """

    code: http.HTTPStatus = http.HTTPStatus.UNAUTHORIZED

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message)


class ForbiddenError(GeometryException):
    """
    Raised when access is forbidden for authenticated users.

    For example, to raise when user lacks permission:
    >>> raise ForbiddenError("Access forbidden")
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

    For example, to raise when env var is missing:
    >>> raise ConfigurationError("DATA_BUCKET_NAME environment variable is required")
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

    For example, to raise when get() finds no record:
    >>> raise RecordNotFoundError("Job xyz not found in data/user/jobs")
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


class StepNotHandledError(GeometryException):
    """
    Raised when the job's step_name has no registered step class.
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Step cannot be handled"):
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


class PolygonNotSimpleError(GeometryException):
    """
    Raised when a polygon is not simple: a vertex has other than exactly 2 edges.
    In a simple closed polygon every vertex has exactly 2 edges; 1 edge means a
    dangling end, 3+ edges mean a branch or self-touch.
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Polygon is not simple: every vertex must have exactly 2 edges"):
        super().__init__(message)


class PolygonValidationError(GeometryException):
    """
    Raised when polygon validation fails (e.g. boundary not convex, obstacle not contained).
    Used by JobMutation after calling PolygonValidation to fail fast on invalid input.

    For example, to raise when validation fails:
    >>> raise PolygonValidationError("Polygon validation failed: polygon.convex")
    """

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Polygon validation failed"):
        super().__init__(message)


class InternalServerError(GeometryException):
    """
    Raised for infrastructure or unexpected errors. User-facing message must not
    expose internal details (e.g. S3, SQS). Used when re-raising after catching
    ServiceUnavailableError or generic Exception in the interceptor.
    """

    code: http.HTTPStatus = http.HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "An error occurred"):
        super().__init__(message)


class AuthHeaderRequiredError(UnauthorizedError):
    """X-Auth header is required."""

    def __init__(self, message: str = "Auth header is required"):
        super().__init__(message)


class TokenExpiredError(UnauthorizedError):
    """JWT token has expired."""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)


class InvalidTokenError(UnauthorizedError):
    """JWT token is invalid."""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class TokenMissingEmailClaimError(UnauthorizedError):
    """JWT token missing email claim."""

    def __init__(self, message: str = "Token missing email claim"):
        super().__init__(message)


class BoundaryRequiredError(ValidationError):
    """Boundary is required and must be a list of points."""

    def __init__(self, message: str = "boundary is required and must be a list of points"):
        super().__init__(message)


class ObstaclesMustBeListError(ValidationError):
    """Obstacles must be a list of obstacle polygons."""

    def __init__(self, message: str = "obstacles must be a list of obstacle polygons"):
        super().__init__(message)


class TitleMustBeStringError(ValidationError):
    """Title must be a string."""

    def __init__(self, message: str = "title must be a string"):
        super().__init__(message)


class MetaRequiredError(ValidationError):
    """Meta is required."""

    def __init__(self, message: str = "meta is required"):
        super().__init__(message)


class MetaMustBeDictError(ValidationError):
    """Meta must be a dict."""

    def __init__(self, message: str = "meta must be a dict"):
        super().__init__(message)


class MetaKeysMustBeStringsError(ValidationError):
    """Meta keys must be strings."""

    def __init__(self, message: str = "meta keys must be strings"):
        super().__init__(message)


class MetaValuesMustBeStringsError(ValidationError):
    """Meta values must be strings."""

    def __init__(self, message: str = "meta values must be strings"):
        super().__init__(message)


class JobNotFinishedToPublishError(ValidationError):
    """Job must be successfully finished to publish."""

    def __init__(self, message: str = "Job must be successfully finished to publish"):
        super().__init__(message)


class JobStdoutMissingGeometryError(ValidationError):
    """Job stdout has no boundary or obstacles; cannot publish gallery."""

    def __init__(self, message: str = "Job stdout has no boundary or obstacles; cannot publish gallery"):
        super().__init__(message)


class UserNotAuthenticatedError(UnauthorizedError):
    """User must be authenticated."""

    def __init__(self, message: str = "User must be authenticated"):
        super().__init__(message)


class ValidationBoundaryRequiredError(ValidationError):
    """Boundary is required (validation endpoint)."""

    def __init__(self, message: str = "boundary is required"):
        super().__init__(message)


class ValidationBoundaryMustBeListError(ValidationError):
    """Boundary must be a list of points or an object with key 'points'."""

    def __init__(self, message: str = "boundary must be a list of points or an object with key 'points'"):
        super().__init__(message)


class ValidationObstaclesMustBeListError(ValidationError):
    """Obstacles must be a list of obstacle polygons (validation endpoint)."""

    def __init__(self, message: str = "obstacles must be a list of obstacle polygons"):
        super().__init__(message)


class ValidationBoundaryNotCCWError(ValidationError):
    """Boundary polygon must be counter-clockwise (CCW)."""

    def __init__(self, message: str = "boundary must be counter-clockwise (CCW)"):
        super().__init__(message)


class ValidationObstacleNotCWError(ValidationError):
    """Obstacle polygon must be clockwise (CW)."""

    def __init__(self, message: str = "obstacle must be clockwise (CW)"):
        super().__init__(message)


class PolygonItemMustBePointError(ValidationError):
    """Polygon item at index must be a Point."""

    def __init__(self, message: str = "Polygon item must be a Point"):
        super().__init__(message)


class PolygonBoxRequiresOnePointError(ValidationError):
    """Polygon.box requires at least one point."""

    def __init__(self, message: str = "Polygon.box requires at least one point"):
        super().__init__(message)


class PolygonUnserializeExpectsListError(ValidationError):
    """Polygon.unserialize expects a list of points."""

    def __init__(self, message: str = "Polygon.unserialize expects a list of points"):
        super().__init__(message)


class PolygonsDoNotShareEdgeError(ValidationError):
    """Polygons do not share an edge."""

    def __init__(self, message: str = "Polygons do not share an edge"):
        super().__init__(message)


class CoordinatorStepRequiresChildrenError(GeometryException):
    """CoordinatorStep requires the job to have children."""

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "CoordinatorStep requires children"):
        super().__init__(message)


class SequenceStepRequiresParentError(GeometryException):
    """SequenceStep requires the job to have a parent."""

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "SequenceStep requires parent"):
        super().__init__(message)


class SequenceStepJobNotInSiblingsError(GeometryException):
    """Job is not part of parent's children (siblings)."""

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "Job not in siblings"):
        super().__init__(message)


class MonitorStepRequiresChildrenError(GeometryException):
    """MonitorStep requires the job to have children."""

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "MonitorStep requires children"):
        super().__init__(message)


class ParallelStepRequiresParentError(GeometryException):
    """ParallelStep requires the job to have a parent."""

    code: http.HTTPStatus = http.HTTPStatus.BAD_REQUEST

    def __init__(self, message: str = "ParallelStep requires parent"):
        super().__init__(message)
