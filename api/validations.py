"""
Validations: polygon geometry validation and base classes.

Title
-----
Validations Module

Context
-------
Validations extend Controller for read-only validation operations.
PolygonValidation validates boundary and obstacles (convex, CCW/CW,
simplicity, contained, overlaps) and returns a status/note dict. Used by
POST v1/polygon and by JobMutation for fail-fast validation.

Examples:
>>> from validations import PolygonValidation
>>> v = PolygonValidation()
>>> result = v.handler(body={"boundary": [...], "obstacles": [...]})
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any
from typing import cast

from controllers import Controller
from controllers import ControllerRequest
from controllers import ControllerResponse
from enums import Status
from exceptions import ValidationError
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


# PolygonValidation returns a dict: keys like "polygon.convex", "obstacles.0.contained";
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


class Validation(Controller):
    """
    Base validation: validate (shallow), execute (deep validations), handler from Controller.

    For example, to run polygon validation:
    >>> v = PolygonValidation()
    >>> result = v.handler({"boundary": [...], "obstacles": []})
    >>> "polygon.convex" in result
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
    Validates boundary polygon and obstacles: convexity, orientation, simplicity,
    containment, and obstacle-overlap. Returns dict of status and note keys.

    For example, to validate boundary and obstacles before creating a job:
    >>> v = PolygonValidation()
    >>> result = v.handler({"boundary": [[0,0],[10,0],[10,10],[0,10]], "obstacles": []})
    >>> result["polygon.convex"]
    'success'
    """

    def validate(self, body: dict[str, Any]) -> PolygonValidationRequest:
        """Shallow validation: require boundary and obstacles; accept list or { points: list }; unserialize to Polygon and Table."""
        boundary: Any = body.get("boundary")
        obstacles: Any = body.get("obstacles")
        if boundary is None:
            raise ValidationError("boundary is required")
        if isinstance(boundary, dict) and "points" in boundary:
            boundary = boundary["points"]
        if not isinstance(boundary, list):
            raise ValidationError("boundary must be a list of points or an object with key 'points'")
        if obstacles is not None and not isinstance(obstacles, list):
            raise ValidationError("obstacles must be a list of obstacle polygons")
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

    def validate_boundary_convex(self, boundary: Polygon) -> ValidationResult:
        """Check boundary convexity. Returns status and note keys."""
        result: ValidationResult = {}
        try:
            convex: bool = boundary.is_convex()
            status: Status = Status.SUCCESS if convex else Status.FAILED
            result["polygon.convex"] = status
            result["polygon.convex.note"] = "Polygon is convex." if convex else "Polygon is not convex."
        except Exception as e:
            logger.debug("PolygonValidation.execute() | polygon.convex error: %s", e)
            result["polygon.convex"] = Status.PENDING
            result["polygon.convex.note"] = "Check skipped (invalid or earlier error)."
        return result

    def validate_boundary_ccw(self, boundary: Polygon) -> ValidationResult:
        """Check boundary is counter-clockwise. Returns status and note keys."""
        result: ValidationResult = {}
        try:
            ccw: bool = boundary.is_ccw()
            status: Status = Status.SUCCESS if ccw else Status.FAILED
            result["polygon.ccw"] = status
            result["polygon.ccw.note"] = "Polygon is counter-clockwise." if ccw else "Polygon is not counter-clockwise."
        except Exception as e:
            logger.debug("PolygonValidation.execute() | polygon.ccw error: %s", e)
            result["polygon.ccw"] = Status.PENDING
            result["polygon.ccw.note"] = "Check skipped (invalid or earlier error)."
        return result

    def validate_boundary_simplicity(self, boundary: Polygon) -> ValidationResult:
        """Check boundary is simple (no self-intersection). Returns status and note keys."""
        result: ValidationResult = {}
        try:
            simple: bool = boundary.is_simple()
            status: Status = Status.SUCCESS if simple else Status.FAILED
            result["polygon.simplicity"] = status
            result["polygon.simplicity.note"] = "Polygon is simple (no self-intersection)." if simple else "Polygon is not simple (self-intersects)."
        except Exception as e:
            logger.debug("PolygonValidation.execute() | polygon.simplicity error: %s", e)
            result["polygon.simplicity"] = Status.PENDING
            result["polygon.simplicity.note"] = "Check skipped (invalid or earlier error)."
        return result

    def validate_obstacles_convex(self, obstacles: Table[Polygon]) -> ValidationResult:
        """Check each obstacle is convex. Returns status and note keys per obstacle."""
        result: ValidationResult = {}
        obstacles_list: list[Polygon] = list(obstacles)
        for idx, obs in enumerate(obstacles_list):
            prefix: str = f"obstacles.{idx}"
            try:
                convex: bool = obs.is_convex()
                status: Status = Status.SUCCESS if convex else Status.FAILED
                result[f"{prefix}.convex"] = status
                result[f"{prefix}.convex.note"] = "Obstacle is convex." if convex else "Obstacle is not convex."
            except Exception as e:
                logger.debug("PolygonValidation.execute() | %s.convex error: %s", prefix, e)
                result[f"{prefix}.convex"] = Status.PENDING
                result[f"{prefix}.convex.note"] = "Check skipped (invalid or earlier error)."
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
                result[f"{prefix}.cw.note"] = "Obstacle is clockwise." if cw else "Obstacle is not clockwise."
            except Exception as e:
                logger.debug("PolygonValidation.execute() | %s.cw error: %s", prefix, e)
                result[f"{prefix}.cw"] = Status.PENDING
                result[f"{prefix}.cw.note"] = "Check skipped (invalid or earlier error)."
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
                    "Obstacle is fully inside the boundary." if contained else "Obstacle is not fully inside the boundary."
                )
            except Exception as e:
                logger.debug("PolygonValidation.execute() | %s.contained error: %s", prefix, e)
                result[f"{prefix}.contained"] = Status.PENDING
                result[f"{prefix}.contained.note"] = "Check skipped (invalid or earlier error)."
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
                result[f"{prefix}.overlaps.note"] = "Obstacle overlaps another obstacle." if overlaps_another else "Obstacle does not overlap others."
            except Exception as e:
                logger.debug("PolygonValidation.execute() | %s.overlaps error: %s", prefix, e)
                result[f"{prefix}.overlaps"] = Status.PENDING
                result[f"{prefix}.overlaps.note"] = "Check skipped (invalid or earlier error)."
        return result

    def execute(self, validated_input: ValidationRequest) -> ValidationResponse:
        """Run deep validations by merging all validate_* results; keep execute simple."""
        req: PolygonValidationRequest = cast(PolygonValidationRequest, validated_input)
        boundary: Polygon = req["boundary"]
        obstacles: Table[Polygon] = req["obstacles"]

        results: list[ValidationResult] = [
            self.validate_boundary_convex(boundary),
            self.validate_boundary_ccw(boundary),
            self.validate_boundary_simplicity(boundary),
            self.validate_obstacles_convex(obstacles),
            self.validate_obstacles_cw(obstacles),
            self.validate_obstacles_contained(boundary, obstacles),
            self.validate_obstacles_overlaps(obstacles),
        ]
        out: PolygonValidationResponse = {}
        for r in results:
            out.update(_normalize_result(r))
        return cast(ValidationResponse, out)
