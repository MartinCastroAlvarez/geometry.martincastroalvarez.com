"""Tests for validations package."""

from enums import Status
from exceptions import ValidationError
from geometry import Polygon
from structs import Table
from validations import PolygonValidation
from validations import PolygonValidationRequest
from validations import PolygonValidationResponse
from validations import ValidationResult


class TestValidationResult:
    """Test ValidationResult type and normalization."""

    def test_validation_result_can_hold_status_and_str(self):
        r: ValidationResult = {
            "polygon.ccw": Status.SUCCESS,
            "polygon.ccw.note": "Polygon is counter-clockwise.",
        }
        assert r["polygon.ccw"] == Status.SUCCESS
        assert r["polygon.ccw.note"] == "Polygon is counter-clockwise."


class TestPolygonValidationValidate:
    """Test PolygonValidation.validate() (shallow validation)."""

    def test_validate_requires_boundary(self):
        v = PolygonValidation()
        try:
            v.validate({"obstacles": []})
            assert False, "expected ValidationError"
        except ValidationError as e:
            assert "boundary" in str(e).lower()

    def test_validate_accepts_list_boundary(self):
        v = PolygonValidation()
        body = {"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []}
        req = v.validate(body)
        assert isinstance(req, dict)
        assert "boundary" in req and "obstacles" in req
        assert isinstance(req["boundary"], Polygon)
        assert isinstance(req["obstacles"], Table)

    def test_validate_accepts_points_object_boundary(self):
        v = PolygonValidation()
        body = {"boundary": {"points": [[0, 0], [1, 0], [1, 1], [0, 1]]}, "obstacles": []}
        req = v.validate(body)
        assert "boundary" in req
        assert len(list(req["boundary"])) == 4

    def test_validate_rejects_non_list_obstacles(self):
        v = PolygonValidation()
        try:
            v.validate({"boundary": [[0, 0], [1, 0], [1, 1]], "obstacles": "not-a-list"})
            assert False, "expected ValidationError"
        except ValidationError as e:
            assert "obstacles" in str(e).lower()


class TestPolygonValidationValidateMethods:
    """Test individual validate_* methods return ValidationResult."""

    def test_validate_boundary_ccw_returns_validation_result(self):
        v = PolygonValidation()
        boundary = Polygon.unserialize([[0, 0], [10, 0], [10, 10], [0, 10]])
        result = v.validate_boundary_ccw(boundary)
        assert "polygon.ccw" in result
        assert "polygon.ccw.note" in result

    def test_validate_boundary_simplicity_returns_validation_result(self):
        v = PolygonValidation()
        boundary = Polygon.unserialize([[0, 0], [10, 0], [10, 10], [0, 10]])
        result = v.validate_boundary_simplicity(boundary)
        assert "polygon.simplicity" in result
        assert "polygon.simplicity.note" in result

    def test_validate_obstacles_simplicity_returns_validation_result(self):
        v = PolygonValidation()
        obstacles = Table.unserialize([Polygon.unserialize([[1, 1], [2, 1], [2, 2], [1, 2]])])
        result = v.validate_obstacles_simplicity(obstacles)
        assert "obstacles.0.simplicity" in result
        assert "obstacles.0.simplicity.note" in result

    def test_validate_obstacles_cw_returns_validation_result(self):
        v = PolygonValidation()
        obstacles = Table.unserialize([Polygon.unserialize([[1, 1], [1, 2], [2, 2], [2, 1]])])
        result = v.validate_obstacles_cw(obstacles)
        assert "obstacles.0.cw" in result
        assert "obstacles.0.cw.note" in result

    def test_validate_obstacles_contained_returns_validation_result(self):
        v = PolygonValidation()
        boundary = Polygon.unserialize([[0, 0], [10, 0], [10, 10], [0, 10]])
        obstacles = Table.unserialize([Polygon.unserialize([[1, 1], [2, 1], [2, 2], [1, 2]])])
        result = v.validate_obstacles_contained(boundary, obstacles)
        assert "obstacles.0.contained" in result
        assert "obstacles.0.contained.note" in result

    def test_validate_obstacles_overlaps_returns_validation_result(self):
        v = PolygonValidation()
        obstacles = Table.unserialize(
            [
                Polygon.unserialize([[1, 1], [2, 1], [2, 2], [1, 2]]),
                Polygon.unserialize([[3, 3], [4, 3], [4, 4], [3, 4]]),
            ]
        )
        result = v.validate_obstacles_overlaps(obstacles)
        assert "obstacles.0.overlaps" in result
        assert "obstacles.1.overlaps" in result

    def test_validate_boundary_ccw_exception_returns_pending(self):
        """When boundary.is_ccw() raises, result is PENDING."""
        v = PolygonValidation()
        boundary = Polygon.unserialize([[0, 0], [10, 0], [10, 10], [0, 10]])

        def raise_err():
            raise RuntimeError("bad")

        boundary.is_ccw = raise_err
        result = v.validate_boundary_ccw(boundary)
        assert result["polygon.ccw"] == Status.PENDING

    def test_validate_obstacles_contained_exception_returns_pending(self):
        """When boundary.contains(obs) raises, result is PENDING for that obstacle."""
        v = PolygonValidation()
        boundary = Polygon.unserialize([[0, 0], [10, 0], [10, 10], [0, 10]])
        obstacles = Table.unserialize([Polygon.unserialize([[1, 1], [2, 1], [2, 2], [1, 2]])])

        def raise_bad(other):
            raise RuntimeError("bad")

        boundary.contains = raise_bad
        result = v.validate_obstacles_contained(boundary, obstacles)
        assert result["obstacles.0.contained"] == Status.PENDING


class TestPolygonValidationExecute:
    """Test PolygonValidation.execute() merges validate_* results."""

    def test_execute_returns_dict_str_str(self):
        v = PolygonValidation()
        body = {"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []}
        req: PolygonValidationRequest = v.validate(body)
        response = v.execute(req)
        assert isinstance(response, dict)
        for k, val in response.items():
            assert isinstance(k, str)
            assert isinstance(val, str), f"expected str for {k!r}, got {type(val)}"

    def test_execute_includes_boundary_ccw_check(self):
        v = PolygonValidation()
        body = {"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []}
        result: PolygonValidationResponse = v.handler(body)
        assert "polygon.ccw" in result
        assert result["polygon.ccw"] in ("success", "failed", "pending")
        assert "polygon.ccw.note" in result

    def test_execute_ccw_boundary_is_success(self):
        v = PolygonValidation()
        body = {"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []}
        result = v.handler(body)
        assert result["polygon.ccw"] == "success"
        assert "counter-clockwise" in result["polygon.ccw.note"].lower() or "ccw" in result["polygon.ccw.note"].lower()

    def test_execute_includes_obstacle_cw_checks_when_obstacles_present(self):
        v = PolygonValidation()
        body = {
            "boundary": [[0, 0], [10, 0], [10, 10], [0, 10]],
            "obstacles": [[[1, 1], [2, 1], [2, 2], [1, 2]]],
        }
        result = v.handler(body)
        assert "obstacles.0.cw" in result
        assert all(isinstance(result[k], str) for k in result)

    def test_execute_includes_status_and_status_note(self):
        """Response always has top-level 'status' and 'status.note' from sub-validations."""
        v = PolygonValidation()
        body = {"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []}
        result = v.handler(body)
        assert "status" in result
        assert "status.note" in result
        assert result["status"] in ("success", "failed", "pending")
        assert isinstance(result["status.note"], str)

    def test_execute_status_success_when_all_checks_pass(self):
        v = PolygonValidation()
        body = {"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []}
        result = v.handler(body)
        assert result["status"] == "success"
        assert "passed" in result["status.note"].lower() or "all" in result["status.note"].lower()

    def test_execute_status_failed_when_any_check_fails(self):
        v = PolygonValidation()
        # Clockwise rectangle -> ccw check fails
        body = {"boundary": [[0, 0], [0, 10], [10, 10], [10, 0]], "obstacles": []}
        result = v.handler(body)
        assert result["status"] == "failed"
        assert "polygon.ccw" in result
        assert result["polygon.ccw"] == "failed"


class TestPolygonValidationHandler:
    """Test full handler flow."""

    def test_handler_validate_then_execute(self):
        v = PolygonValidation()
        body = {"boundary": [[0, 0], [10, 0], [10, 10], [0, 10]], "obstacles": []}
        result = v.handler(body)
        assert isinstance(result, dict)
        assert "polygon.ccw" in result
        assert result["polygon.ccw"] == "success"

    def test_handler_raises_on_invalid_body(self):
        v = PolygonValidation()
        try:
            v.handler({})
            assert False, "expected ValidationError"
        except ValidationError:
            pass
