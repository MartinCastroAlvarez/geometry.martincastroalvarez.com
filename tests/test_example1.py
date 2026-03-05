"""
Test that api/steps.py runs the full pipeline for lab/example1.py gallery (L-shape, 2 holes).
Expects 4 guards for sufficient coverage.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import Polygon
from models import Job
from models import User
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep
from tests.utils import assert_convex_components_simple_convex_no_obstacle_intersection
from tests.utils import assert_convex_components_visibility_within_component
from tests.utils import assert_ears_no_obstacle_intersection
from tests.utils import assert_ears_simple_and_convex
from tests.utils import assert_no_redundant_guards
from tests.utils import print_guard_coverage_report


def _user():
    return User(email=Email("u@e.com"))


# From lab/example1.py: polygon + holes (API uses boundary + obstacles)
EXAMPLE1_STDIN = {
    "boundary": [
        ["0.0", "0.0"],
        ["10.0", "0.0"],
        ["10.0", "5.0"],
        ["15.0", "5.0"],
        ["15.0", "10.0"],
        ["10.0", "10.0"],
        ["10.0", "15.0"],
        ["5.0", "15.0"],
        ["5.0", "10.0"],
        ["0.0", "10.0"],
    ],
    "obstacles": [
        [["2.0", "4.0"], ["4.0", "4.0"], ["4.0", "2.0"], ["2.0", "2.0"]],
        [["6.0", "14.0"], ["8.0", "14.0"], ["8.0", "12.0"], ["6.0", "12.0"]],
    ],
}


def test_example1_full_pipeline_requires_three_guards():
    stdout = {}
    job_validate = Job(id=Identifier("ex1-v"), step_name=StepName.VALIDATE_POLYGONS, stdin=dict(EXAMPLE1_STDIN))
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(id=Identifier("ex1-s"), step_name=StepName.STITCHING, stdin=dict(EXAMPLE1_STDIN), stdout=dict(stdout))
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    stitched = Polygon.unserialize(stdout["stitched"])
    assert stitched.is_simple(), (
        f"Stitched polygon must be simple; got stitched with {len(stitched)} vertices"
    )
    job_ear = Job(id=Identifier("ex1-e"), step_name=StepName.EAR_CLIPPING, stdin=dict(EXAMPLE1_STDIN), stdout=dict(stdout))
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    assert_ears_simple_and_convex(stdout["ears"])
    assert_ears_no_obstacle_intersection(stdout["ears"], stdout["obstacles"])
    job_convex = Job(id=Identifier("ex1-c"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION, stdin=dict(EXAMPLE1_STDIN), stdout=dict(stdout))
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())
    assert_convex_components_simple_convex_no_obstacle_intersection(
        stdout["convex_components"], stdout["obstacles"]
    )
    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )
    job_guard = Job(id=Identifier("ex1-g"), step_name=StepName.GUARD_PLACEMENT, stdin=dict(EXAMPLE1_STDIN), stdout=dict(stdout))
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert len(guard_out["guards"]) == 5, f"Example1 expects 5 guards; got {len(guard_out['guards'])}"
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Example1 guard coverage report")
