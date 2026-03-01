"""
Validations: polygon geometry validation and base classes.

Title
-----
Validations Module

Context
-------
Validations extend Controller for read-only validation operations.
PolygonValidation validates that the boundary is CCW and obstacles are CW; returns a status/note dict. Used by
POST v1/polygon and by JobMutation for fail-fast validation.

Examples:
>>> from validations import PolygonValidation
>>> v = PolygonValidation()
>>> result = v.handler(body={"boundary": [...], "obstacles": [...]})
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from collections import Counter
from typing import Any
from typing import cast

from controllers import Controller
from controllers import ControllerRequest
from controllers import ControllerResponse
from enums import PolygonValidationCode
from enums import Status
from exceptions import ValidationBoundaryMustBeListError
from exceptions import ValidationBoundaryRequiredError
from exceptions import ValidationObstaclesMustBeListError
from geometry import Polygon
from structs import Table

logger = logging.getLogger(__name__)


class ValidationRequest(ControllerRequest):
    """Base for validation requests."""

    pass


class PolygonValidationRequest(ValidationRequest):
    """Validate polygon: boundary and obstacles (same shape as job create)."""

    boundary: Polygon
    obstacles: Table[Polygon]


class ValidationResponse(ControllerResponse):
    """Base for validation responses."""

    pass


# PolygonValidation returns a dict: keys like "polygon.ccw", "obstacles.0.cw";
# values are str (status.value for status keys, message for *.note keys) for JSON serialization.
PolygonValidationResponse = dict[str, str]


# Internal result from each validate_* method: keys are check names, values are Status or note string.
ValidationResult = dict[str, str | Status]


def _normalize_result(result: ValidationResult) -> dict[str, str]:
    """Convert ValidationResult to PolygonValidationResponse (Status -> status.value)."""
    out: dict[str, str] = {}
    for k, v in result.items():
        out[k] = v.value if isinstance(v, Status) else v
    return out


def _point_tuple(p: Any) -> tuple[float, float] | None:
    """Normalize a point-like item to (x, y). Returns None if not a valid point."""
    if isinstance(p, (list, tuple)) and len(p) >= 2:
        try:
            return (float(p[0]), float(p[1]))
        except (TypeError, ValueError):
            return None
    if isinstance(p, dict) and "x" in p and "y" in p:
        try:
            return (float(p["x"]), float(p["y"]))
        except (TypeError, ValueError):
            return None
    return None


def _points_have_degree_gt2(points: list[Any]) -> bool:
    """True if any point (by coordinates) appears more than once (degree > 2 in closed polygon)."""
    tuples: list[tuple[float, float]] = []
    for p in points:
        t = _point_tuple(p)
        if t is not None:
            tuples.append(t)
    if not tuples:
        return False
    counts = Counter(tuples)
    return any(c > 1 for c in counts.values())


def _status_values(merged: ValidationResult) -> list[Status]:
    """Extract status values from merged (status keys only; values may be Status or str)."""
    out: list[Status] = []
    for k, v in merged.items():
        if k.endswith(".note"):
            continue
        if isinstance(v, Status):
            out.append(v)
        elif isinstance(v, str) and v in ("success", "failed", "pending"):
            out.append(Status(v))
    return out


def _overall_status(merged: ValidationResult) -> Status:
    """
    Compute overall status from all status keys in merged result.
    Uses only keys whose value is a Status or status string (not *.note string keys).
    SUCCESS only if every such value is Status.SUCCESS; else PENDING if any is PENDING; else FAILED.
    """
    status_values = _status_values(merged)
    if not status_values:
        return Status.PENDING
    if all(s == Status.SUCCESS for s in status_values):
        return Status.SUCCESS
    if any(s == Status.PENDING for s in status_values):
        return Status.PENDING
    return Status.FAILED


class Validation(Controller):
    """
    Base validation: validate (shallow), execute (deep validations), handler from Controller.

    For example, to run polygon validation:
    >>> v = PolygonValidation()
    >>> result = v.handler({"boundary": [...], "obstacles": []})
    >>> "polygon.ccw" in result
    True
    """

    @abstractmethod
    def validate(self, body: dict[str, Any]) -> ValidationRequest:
        """Validate input shape and types; return typed request. Raises on invalid."""
        pass

    @abstractmethod
    def execute(self, validated_input: ValidationRequest) -> ValidationResponse:
        """Run deep validations and return result dict (e.g. status + notes per check)."""
        pass


class PolygonValidation(Validation):
    """
    Validates boundary polygon and obstacles: boundary must be CCW, each obstacle must be CW.
    Returns dict of status and note keys.

    For example, to validate boundary and obstacles before creating a job:
    >>> v = PolygonValidation()
    >>> result = v.handler({"boundary": [[0,0],[10,0],[10,10],[0,10]], "obstacles": []})
    >>> result["polygon.ccw"]
    'success'
    """

    def validate(self, body: dict[str, Any]) -> PolygonValidationRequest:
        """Shallow validation: require boundary and obstacles; accept list or { points: list }; unserialize to Polygon and Table."""
        boundary: Any = body.get("boundary")
        obstacles: Any = body.get("obstacles")
        if boundary is None:
            raise ValidationBoundaryRequiredError("boundary is required")
        if isinstance(boundary, dict) and "points" in boundary:
            boundary = boundary["points"]
        if not isinstance(boundary, list):
            raise ValidationBoundaryMustBeListError("boundary must be a list of points or an object with key 'points'")
        if obstacles is not None and not isinstance(obstacles, list):
            raise ValidationObstaclesMustBeListError("obstacles must be a list of obstacle polygons")
        obstacle_list: list[Any] = obstacles or []
        obstacle_polys: list[Polygon] = []
        for obs in obstacle_list:
            if isinstance(obs, dict) and "points" in obs:
                obs = obs["points"]
            if isinstance(obs, list):
                obstacle_polys.append(Polygon.unserialize(obs))
        boundary_poly: Polygon = Polygon.unserialize(boundary)
        obstacles_table: Table[Polygon] = Table.unserialize(obstacle_polys)
        return PolygonValidationRequest(boundary=boundary_poly, obstacles=obstacles_table)

    def validate_vertex_degree_raw(self, body: dict[str, Any]) -> ValidationResult:
        """
        Check boundary and obstacles for repeated vertices (degree > 2).
        Runs on raw body so we can report this before Polygon construction would raise.
        """
        result: ValidationResult = {}
        boundary: Any = body.get("boundary")
        obstacles: Any = body.get("obstacles")
        if boundary is not None:
            if isinstance(boundary, dict) and "points" in boundary:
                boundary = boundary["points"]
            if isinstance(boundary, list):
                has_repeated = _points_have_degree_gt2(boundary)
                status: Status = Status.FAILED if has_repeated else Status.SUCCESS
                result["polygon.vertex_degree"] = status
                result["polygon.vertex_degree.note"] = (
                    PolygonValidationCode.POLYGON_VERTEX_DEGREE_GT2.value if has_repeated else PolygonValidationCode.POLYGON_VERTEX_DEGREE_OK.value
                )
        obstacle_list: list[Any] = obstacles if isinstance(obstacles, list) else []
        for idx, obs in enumerate(obstacle_list):
            prefix: str = f"obstacles.{idx}"
            points: Any = obs["points"] if isinstance(obs, dict) and "points" in obs else obs
            if not isinstance(points, list):
                result[f"{prefix}.vertex_degree"] = Status.PENDING
                result[f"{prefix}.vertex_degree.note"] = PolygonValidationCode.CHECK_SKIPPED.value
                continue
            has_repeated = _points_have_degree_gt2(points)
            status = Status.FAILED if has_repeated else Status.SUCCESS
            result[f"{prefix}.vertex_degree"] = status
            result[f"{prefix}.vertex_degree.note"] = (
                PolygonValidationCode.OBSTACLE_VERTEX_DEGREE_GT2.value if has_repeated else PolygonValidationCode.OBSTACLE_VERTEX_DEGREE_OK.value
            )
        return result

    def handler(self, body: dict[str, Any]) -> ValidationResponse:
        """Run vertex-degree check first (on raw body), then validate + execute; merge results."""
        degree_result: ValidationResult = self.validate_vertex_degree_raw(body)
        degree_failed = any(v == Status.FAILED for k, v in degree_result.items() if not k.endswith(".note") and isinstance(v, Status))
        if degree_failed:
            merged: ValidationResult = dict(degree_result)
            merged["status"] = Status.FAILED
            merged["status.note"] = PolygonValidationCode.VALIDATIONS_FAILED_OR_PENDING.value
            return cast(ValidationResponse, _normalize_result(merged))
        validated_input = self.validate(body)
        exec_result: ValidationResult = dict(self.execute(validated_input))
        for k, v in degree_result.items():
            exec_result[k] = v
        overall = _overall_status(exec_result)
        exec_result["status"] = overall
        exec_result["status.note"] = (
            PolygonValidationCode.ALL_VALIDATIONS_PASSED.value
            if overall == Status.SUCCESS
            else PolygonValidationCode.VALIDATIONS_FAILED_OR_PENDING.value
        )
        return cast(ValidationResponse, _normalize_result(exec_result))

    def validate_boundary_ccw(self, boundary: Polygon) -> ValidationResult:
        """Check boundary is counter-clockwise. Returns status and note keys."""
        result: ValidationResult = {}
        try:
            ccw: bool = boundary.is_ccw()
            status: Status = Status.SUCCESS if ccw else Status.FAILED
            result["polygon.ccw"] = status
            result["polygon.ccw.note"] = PolygonValidationCode.POLYGON_CCW_OK.value if ccw else PolygonValidationCode.POLYGON_NOT_CCW.value
        except Exception as e:
            logger.debug("PolygonValidation.execute() | polygon.ccw error: %s", e)
            result["polygon.ccw"] = Status.PENDING
            result["polygon.ccw.note"] = PolygonValidationCode.CHECK_SKIPPED.value
        return result

    def validate_boundary_simplicity(self, boundary: Polygon) -> ValidationResult:
        """Check boundary is simple (no self-intersection). Returns status and note keys."""
        result: ValidationResult = {}
        try:
            simple: bool = boundary.is_simple()
            status: Status = Status.SUCCESS if simple else Status.FAILED
            result["polygon.simplicity"] = status
            result["polygon.simplicity.note"] = (
                PolygonValidationCode.POLYGON_SIMPLE_OK.value if simple else PolygonValidationCode.POLYGON_NOT_SIMPLE.value
            )
        except Exception as e:
            logger.debug("PolygonValidation.execute() | polygon.simplicity error: %s", e)
            result["polygon.simplicity"] = Status.PENDING
            result["polygon.simplicity.note"] = PolygonValidationCode.CHECK_SKIPPED.value
        return result

    def validate_obstacles_simplicity(self, obstacles: Table[Polygon]) -> ValidationResult:
        """Check each obstacle is simple (no self-intersection). Returns status and note keys per obstacle."""
        result: ValidationResult = {}
        obstacles_list: list[Polygon] = list(obstacles)
        for idx, obs in enumerate(obstacles_list):
            prefix: str = f"obstacles.{idx}"
            try:
                simple: bool = obs.is_simple()
                status: Status = Status.SUCCESS if simple else Status.FAILED
                result[f"{prefix}.simplicity"] = status
                result[f"{prefix}.simplicity.note"] = (
                    PolygonValidationCode.OBSTACLE_SIMPLE_OK.value if simple else PolygonValidationCode.OBSTACLE_NOT_SIMPLE.value
                )
            except Exception as e:
                logger.debug("PolygonValidation.execute() | %s.simplicity error: %s", prefix, e)
                result[f"{prefix}.simplicity"] = Status.PENDING
                result[f"{prefix}.simplicity.note"] = PolygonValidationCode.CHECK_SKIPPED.value
        return result

    def validate_obstacles_cw(self, obstacles: Table[Polygon]) -> ValidationResult:
        """Check each obstacle is clockwise. Returns status and note keys per obstacle."""
        result: ValidationResult = {}
        obstacles_list: list[Polygon] = list(obstacles)
        for idx, obs in enumerate(obstacles_list):
            prefix: str = f"obstacles.{idx}"
            try:
                cw: bool = obs.is_cw()
                status: Status = Status.SUCCESS if cw else Status.FAILED
                result[f"{prefix}.cw"] = status
                result[f"{prefix}.cw.note"] = PolygonValidationCode.OBSTACLE_CW_OK.value if cw else PolygonValidationCode.OBSTACLE_NOT_CW.value
            except Exception as e:
                logger.debug("PolygonValidation.execute() | %s.cw error: %s", prefix, e)
                result[f"{prefix}.cw"] = Status.PENDING
                result[f"{prefix}.cw.note"] = PolygonValidationCode.CHECK_SKIPPED.value
        return result

    def validate_obstacles_contained(self, boundary: Polygon, obstacles: Table[Polygon]) -> ValidationResult:
        """Check each obstacle is fully inside the boundary. Returns status and note keys per obstacle."""
        result: ValidationResult = {}
        obstacles_list: list[Polygon] = list(obstacles)
        for idx, obs in enumerate(obstacles_list):
            prefix: str = f"obstacles.{idx}"
            try:
                contained: bool = boundary.contains(obs)
                status: Status = Status.SUCCESS if contained else Status.FAILED
                result[f"{prefix}.contained"] = status
                result[f"{prefix}.contained.note"] = (
                    PolygonValidationCode.OBSTACLE_CONTAINED_OK.value if contained else PolygonValidationCode.OBSTACLE_NOT_CONTAINED.value
                )
            except Exception as e:
                logger.debug("PolygonValidation.execute() | %s.contained error: %s", prefix, e)
                result[f"{prefix}.contained"] = Status.PENDING
                result[f"{prefix}.contained.note"] = PolygonValidationCode.CHECK_SKIPPED.value
        return result

    def validate_obstacles_overlaps(self, obstacles: Table[Polygon]) -> ValidationResult:
        """Check no obstacle overlaps another. Returns status and note keys per obstacle."""
        result: ValidationResult = {}
        obstacles_list: list[Polygon] = list(obstacles)
        for idx, obs in enumerate(obstacles_list):
            prefix: str = f"obstacles.{idx}"
            try:
                overlaps_another: bool = any(obs.intersects(other, inclusive=True) for other in obstacles_list if other is not obs)
                status: Status = Status.FAILED if overlaps_another else Status.SUCCESS
                result[f"{prefix}.overlaps"] = status
                result[f"{prefix}.overlaps.note"] = (
                    PolygonValidationCode.OBSTACLE_OVERLAPS.value if overlaps_another else PolygonValidationCode.OBSTACLE_NO_OVERLAP.value
                )
            except Exception as e:
                logger.debug("PolygonValidation.execute() | %s.overlaps error: %s", prefix, e)
                result[f"{prefix}.overlaps"] = Status.PENDING
                result[f"{prefix}.overlaps.note"] = PolygonValidationCode.CHECK_SKIPPED.value
        return result

    def execute(self, validated_input: ValidationRequest) -> ValidationResponse:
        """Run deep validations: boundary must be CCW, obstacles must be CW. Merge results; add status and status.note."""
        req: PolygonValidationRequest = cast(PolygonValidationRequest, validated_input)
        boundary: Polygon = req["boundary"]
        obstacles: Table[Polygon] = req["obstacles"]

        results: list[ValidationResult] = [
            self.validate_boundary_ccw(boundary),
            self.validate_obstacles_cw(obstacles),
        ]
        merged: ValidationResult = {}
        for r in results:
            merged.update(r)
        overall: Status = _overall_status(merged)
        merged["status"] = overall
        merged["status.note"] = (
            PolygonValidationCode.ALL_VALIDATIONS_PASSED.value
            if overall == Status.SUCCESS
            else PolygonValidationCode.VALIDATIONS_FAILED_OR_PENDING.value
        )
        out: PolygonValidationResponse = _normalize_result(merged)
        return cast(ValidationResponse, out)
