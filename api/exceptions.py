"""
Custom exceptions for the geometry (art gallery) API.

All exceptions inherit from GeometryException and set a numeric `code` attribute
used for HTTP status codes (e.g. ValidationError.code == 400). Handlers use
Response.from_error(exception) to build JSON error responses.

Example:

    raise ValidationError("id is required")
    try:
        raise RecordNotFoundError("Job xyz not found")
    except GeometryException as e:
        print(e.code, str(e))
"""


class GeometryException(Exception):
    """
    Base exception for geometry API errors.

    For example, to check the HTTP code:
    >>> e = ValidationError("bad input")
    >>> e.code
    400
    """

    code: int = 500

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message)
        self.message = message


class ValidationError(GeometryException):
    """
    Raised when input validation fails.
    """

    code: int = 400

    def __init__(self, message: str = "Validation failed"):
        super().__init__(message)


class NotFoundError(GeometryException):
    """
    Raised when a requested resource is not found.
    """

    code: int = 404

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)


class UnauthorizedError(GeometryException):
    """
    Raised when authentication is required but missing or invalid.
    """

    code: int = 401

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message)


class ForbiddenError(GeometryException):
    """
    Raised when access is forbidden for authenticated users.
    """

    code: int = 403

    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message)


class ConflictError(GeometryException):
    """
    Raised when a request conflicts with the current state.
    """

    code: int = 409

    def __init__(self, message: str = "Request conflicts with current state"):
        super().__init__(message)


class ServiceUnavailableError(GeometryException):
    """
    Raised when external services are unavailable.
    """

    code: int = 503

    def __init__(self, message: str = "Service temporarily unavailable"):
        super().__init__(message)


class ConfigurationError(GeometryException):
    """
    Raised when there are configuration issues.
    """

    code: int = 500

    def __init__(self, message: str = "Configuration error"):
        super().__init__(message)


class StorageError(GeometryException):
    """
    Raised when stored data or storage response is invalid (not a user input error).
    Use for corrupt/invalid S3 response shape or object content; use ValidationError for bad request input.
    """

    code: int = 500

    def __init__(self, message: str = "Invalid stored data or storage response"):
        super().__init__(message)


class MethodNotAllowedError(GeometryException):
    """
    Raised when a request method is not allowed.
    """

    code: int = 405

    def __init__(self, message: str = "Method not allowed"):
        super().__init__(message)


class RecordNotFoundError(GeometryException):
    """
    Raised when a record is not found.
    """

    code: int = 404

    def __init__(self, message: str = "Record not found"):
        super().__init__(message)


class CorruptionError(GeometryException):
    """
    Raised when a record is corrupted.
    """

    code: int = 409

    def __init__(self, message: str = "Record corrupted"):
        super().__init__(message)


class InvalidActionError(GeometryException):
    """
    Raised when worker action is not 'run' or 'report'.
    """

    code: int = 400

    def __init__(self, message: str = "Action must be 'run' or 'report'"):
        super().__init__(message)


class BoxInvalidEdgeError(GeometryException):
    """
    Raised when a box has invalid edges (e.g. non-vertical or non-horizontal).
    """

    code: int = 400

    def __init__(self, message: str = "Box has invalid edge"):
        super().__init__(message)


class SerializedInvalidDictError(GeometryException):
    """
    Raised when unserializing from an invalid dict (e.g. missing keys or wrong type).
    """

    code: int = 400

    def __init__(self, message: str = "Invalid dict for unserialize"):
        super().__init__(message)


class SequenceMultipleOverlapsError(GeometryException):
    """
    Raised when Sequence.__and__ finds multiple disjoint overlapping regions.
    """

    code: int = 400

    def __init__(self, message: str = "Sequences overlap in multiple places"):
        super().__init__(message)
