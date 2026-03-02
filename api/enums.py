"""
API enums: Action, LogLevel, Method, Orientation, StepName, Status.

Title
-----
Enums Module

Context
-------
This module exports enums used across the API and workers. Method is
HTTP method (OPTIONS, GET, POST, PATCH, DELETE) with parse() that raises
MethodNotAllowedError. Action is worker action (START, REPORT) with parse()
defaulting to START. Status is task status (PENDING, SUCCESS, FAILED).
StepName is job pipeline step name (ART_GALLERY, STITCHING, EAR_CLIPPING, etc.).
Orientation is geometric turn direction (COLLINEAR, CLOCKWISE, COUNTER_CLOCKWISE).
LogLevel is logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) for LOG_LEVEL env.
All have parse() or value coercion where used in request/response.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from exceptions import InvalidActionError
from exceptions import MethodNotAllowedError
from exceptions import ValidationError

if TYPE_CHECKING:
    from attributes import Slug


class Action(str, Enum):
    """
    Worker action: START (default), REPORT.

    For example, to parse an action from a message:
    >>> Action.parse("start")
    <Action.START: 'start'>
    >>> Action.parse(None)
    <Action.START: 'start'>
    """

    START = "start"
    REPORT = "report"

    @classmethod
    def parse(cls, value: str | None) -> Action:
        """
        Coerce string to Action; default START if missing/empty; raises InvalidActionError (400) if invalid.

        For example, to parse from request body:
        >>> action = Action.parse(body.get("action"))
        >>> action == Action.REPORT
        True
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return cls.START
        raw: str = value.strip().lower() if isinstance(value, str) else str(value).strip().lower()
        try:
            return cls(raw)
        except ValueError:
            raise InvalidActionError(f"action must be one of [{cls.START.value!r}, {cls.REPORT.value!r}], got {raw!r}")


class LogLevel(str, Enum):
    """
    Logging level for LOG_LEVEL env. Matches standard library names (DEBUG, INFO, etc.).

    For example, to parse from env:
    >>> LogLevel.parse("info")
    <LogLevel.INFO: 'INFO'>
    >>> LogLevel.parse(None)
    <LogLevel.INFO: 'INFO'>
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def parse(cls, value: str | None) -> LogLevel:
        """
        Coerce string to LogLevel; default INFO if missing/empty; raises ValidationError if invalid.
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return cls.INFO
        raw: str = value.strip().upper() if isinstance(value, str) else str(value).strip().upper()
        try:
            return cls(raw)
        except ValueError:
            allowed = ", ".join(level.value for level in cls)
            raise ValidationError(f"LOG_LEVEL must be one of [{allowed}], got {raw!r}")


class Method(str, Enum):
    """
    HTTP method: OPTIONS, GET, POST, PATCH, DELETE.

    For example, to parse the request method:
    >>> Method.parse("POST")
    <Method.POST: 'POST'>
    """

    OPTIONS = "OPTIONS"
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"

    @classmethod
    def parse(cls, value: str | None) -> Method:
        """
        Coerce string to Method; raises MethodNotAllowedError if invalid or missing.

        For example, to validate HTTP method from event:
        >>> method = Method.parse(event.get("httpMethod"))
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            raise MethodNotAllowedError("HTTP method is required")
        raw: str = value.strip().upper() if isinstance(value, str) else str(value).strip().upper()
        try:
            return cls(raw)
        except ValueError:
            raise MethodNotAllowedError(f"method must be one of [{', '.join(m.value for m in cls)}], got {raw!r}")


class Orientation(int, Enum):
    """
    Geometric turn direction: COLLINEAR (0), CLOCKWISE (-1), COUNTER_CLOCKWISE (1).

    For example, to use in polygon orientation checks:
    >>> Orientation.CLOCKWISE
    <Orientation.CLOCKWISE: -1>
    """

    COLLINEAR = 0
    CLOCKWISE = -1
    COUNTER_CLOCKWISE = 1


class StepName(str, Enum):
    """
    Job pipeline step name.

    For example, to parse step_name from job data:
    >>> StepName.parse("ear_clipping")
    <StepName.EAR_CLIPPING: 'ear_clipping'>
    """

    ART_GALLERY = "art_gallery"
    VALIDATE_POLYGONS = "validate_polygons"
    STITCHING = "stitching"
    EAR_CLIPPING = "ear_clipping"
    CONVEX_COMPONENT_OPTIMIZATION = "convex_component_optimization"
    GUARD_PLACEMENT = "guard_placement"

    @property
    def slug(self) -> Slug:
        """URL-safe slug for this step name (e.g. art_gallery -> art-gallery)."""
        from attributes import Slug

        return Slug(self.value)

    @classmethod
    def parse(cls, value: str | None) -> StepName:
        """
        Coerce string to StepName; raises ValidationError (400) if invalid.

        For example, to parse from job dict:
        >>> step_name = StepName.parse(data.get("step_name"))
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError("step_name is required and must be a non-empty string")
        raw: str = (
            value.strip().lower().replace(" ", "_").replace("-", "_")
            if isinstance(value, str)
            else str(value).strip().lower().replace(" ", "_").replace("-", "_")
        )
        try:
            return cls(raw)
        except ValueError:
            allowed = ", ".join(repr(s.value) for s in cls)
            raise ValidationError(f"step_name must be one of [{allowed}], got {raw!r}")


class Status(str, Enum):
    """
    Task status: PENDING, SUCCESS, or FAILED.

    For example, to check job result:
    >>> Status.parse("success") == Status.SUCCESS
    True
    """

    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

    @classmethod
    def parse(cls, value: str | None) -> Status:
        """
        Coerce string to Status; raises ValidationError (400) if invalid.

        For example, to parse from job response:
        >>> status = Status.parse(job_data.get("status"))
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError("status is required and must be a non-empty string")
        raw: str = value.strip().lower() if isinstance(value, str) else str(value).strip().lower()
        try:
            return cls(raw)
        except ValueError:
            raise ValidationError(f"status must be one of [{cls.PENDING.value!r}, {cls.FAILED.value!r}, {cls.SUCCESS.value!r}], got {raw!r}")


class PolygonValidationCode(str, Enum):
    """
    Polygon validation codes for i18n. Exceptions may carry a string that can be
    converted with PolygonValidationCode.parse(). Frontend uses these to show localized messages.
    """

    POLYGON_CONVEX_OK = "POLYGON_CONVEX_OK"
    POLYGON_NOT_CONVEX = "POLYGON_NOT_CONVEX"
    POLYGON_CCW_OK = "POLYGON_CCW_OK"
    POLYGON_NOT_CCW = "POLYGON_NOT_CCW"
    POLYGON_SIMPLE_OK = "POLYGON_SIMPLE_OK"
    POLYGON_NOT_SIMPLE = "POLYGON_NOT_SIMPLE"
    POLYGON_VERTEX_DEGREE_OK = "POLYGON_VERTEX_DEGREE_OK"
    POLYGON_VERTEX_DEGREE_GT2 = "POLYGON_VERTEX_DEGREE_GT2"
    OBSTACLE_VERTEX_DEGREE_OK = "OBSTACLE_VERTEX_DEGREE_OK"
    OBSTACLE_VERTEX_DEGREE_GT2 = "OBSTACLE_VERTEX_DEGREE_GT2"
    OBSTACLE_CONVEX_OK = "OBSTACLE_CONVEX_OK"
    OBSTACLE_NOT_CONVEX = "OBSTACLE_NOT_CONVEX"
    OBSTACLE_SIMPLE_OK = "OBSTACLE_SIMPLE_OK"
    OBSTACLE_NOT_SIMPLE = "OBSTACLE_NOT_SIMPLE"
    OBSTACLE_CW_OK = "OBSTACLE_CW_OK"
    OBSTACLE_NOT_CW = "OBSTACLE_NOT_CW"
    OBSTACLE_CONTAINED_OK = "OBSTACLE_CONTAINED_OK"
    OBSTACLE_NOT_CONTAINED = "OBSTACLE_NOT_CONTAINED"
    OBSTACLE_OVERLAPS = "OBSTACLE_OVERLAPS"
    OBSTACLE_NO_OVERLAP = "OBSTACLE_NO_OVERLAP"
    CHECK_SKIPPED = "CHECK_SKIPPED"
    ALL_VALIDATIONS_PASSED = "ALL_VALIDATIONS_PASSED"
    VALIDATIONS_FAILED_OR_PENDING = "VALIDATIONS_FAILED_OR_PENDING"

    @classmethod
    def parse(cls, value: str | None) -> PolygonValidationCode:
        """
        Coerce string to PolygonValidationCode; raises ValidationError if invalid.
        Use when an exception contains a string that should be converted to a code.
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError("polygon validation code is required and must be a non-empty string")
        raw: str = value.strip().upper().replace("-", "_") if isinstance(value, str) else str(value).strip().upper().replace("-", "_")
        try:
            return cls(raw)
        except ValueError:
            allowed = ", ".join(repr(c.value) for c in cls)
            raise ValidationError(f"polygon validation code must be one of [{allowed}], got {raw!r}")
