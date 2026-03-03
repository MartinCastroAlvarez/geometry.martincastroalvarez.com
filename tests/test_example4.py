"""
Test that api/steps.py rejects lab/example4.py gallery (20 vertices, 3 holes).
Example4 has invalid input per lab docs: one obstacle is not strictly inside the boundary
(touches or intersects it). Validation is expected to raise ValidationObstacleNotContainedError.
"""

import pytest

from attributes import Email
from attributes import Identifier
from enums import StepName
from exceptions import ValidationObstacleNotContainedError
from models import Job
from models import User
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


EXAMPLE4_STDIN = {
    "boundary": [
        ["0.0", "0.0"],
        ["12.0", "0.0"],
        ["12.0", "4.0"],
        ["16.0", "4.0"],
        ["16.0", "0.0"],
        ["26.0", "0.0"],
        ["26.0", "14.0"],
        ["20.0", "14.0"],
        ["20.0", "10.0"],
        ["14.0", "10.0"],
        ["14.0", "14.0"],
        ["10.0", "14.0"],
        ["10.0", "20.0"],
        ["14.0", "20.0"],
        ["14.0", "24.0"],
        ["6.0", "24.0"],
        ["6.0", "14.0"],
        ["2.0", "14.0"],
        ["2.0", "8.0"],
        ["0.0", "8.0"],
    ],
    "obstacles": [
        [["4.0", "5.0"], ["7.0", "5.0"], ["7.0", "3.0"], ["4.0", "3.0"]],
        [["19.0", "7.0"], ["23.0", "7.0"], ["23.0", "4.0"], ["19.0", "4.0"]],
        [["8.0", "21.0"], ["12.0", "21.0"], ["12.0", "18.0"], ["8.0", "18.0"]],
    ],
}


def test_example4_validation_raises_polygon_not_simple_obstacle_not_inside():
    """
    Example4 has an obstacle not strictly inside the boundary (per lab docs).
    Validation step must raise ValidationObstacleNotContainedError with message about obstacle not strictly inside.
    """
    job_validate = Job(
        id=Identifier("ex4-v"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(EXAMPLE4_STDIN),
    )
    step = ValidationPolygonStep(job=job_validate, user=_user())
    with pytest.raises(ValidationObstacleNotContainedError) as exc_info:
        step.run()
    assert "Obstacle is not strictly inside" in str(exc_info.value)
