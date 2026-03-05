"""
Test that api/steps.py runs the full pipeline for the polygon gallery (boundary + 3 obstacles).
Expects 2 guards for sufficient coverage.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import ConvexComponent
from geometry import Polygon
from models import Job
from tests.utils import assert_convex_components_simple_convex_no_obstacle_intersection
from tests.utils import assert_convex_components_visibility_within_component
from tests.utils import assert_ears_no_obstacle_intersection
from tests.utils import assert_ears_simple_and_convex
from tests.utils import assert_no_redundant_guards
from tests.utils import print_guard_coverage_report
from models import User
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


TRIANGLE_STDIN = {
    "boundary": {
        "points": [
            [619.3310965232191, 482.5],
            [14.007488451252128, 332.5],
            [361.1930950644299, 274.5],
            [358.1914903963044, 9.5],
        ]
    },
    "obstacles": [
        {
            "points": [
                [506.2706540238269, 416.5],
                [506.2706540238269, 333.5],
                [450.2407002188184, 312.5],
                [444.2374908825675, 395.5],
            ]
        },
        {
            "points": [
                [405.21663019693653, 385.5],
                [406.2171650863117, 319.5],
                [269.1438852419159, 343.5],
            ]
        },
        {
            "points": [
                [404.21609530756143, 281.5],
                [463.2476537806954, 276.5],
                [424.22679309506447, 223.5],
            ]
        },
    ],
    "guards": [],
}


def test_triangle_full_pipeline_requires_two_guards():
    stdout = {}
    job_validate = Job(id=Identifier("tri-v"), step_name=StepName.VALIDATE_POLYGONS, stdin=dict(TRIANGLE_STDIN))
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(id=Identifier("tri-s"), step_name=StepName.STITCHING, stdin=dict(TRIANGLE_STDIN), stdout=dict(stdout))
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    stitched = Polygon.unserialize(stdout["stitched"])
    assert stitched.is_simple(), (
        f"Stitched polygon must be simple; got stitched with {len(stitched)} vertices"
    )
    job_ear = Job(id=Identifier("tri-e"), step_name=StepName.EAR_CLIPPING, stdin=dict(TRIANGLE_STDIN), stdout=dict(stdout))
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    assert_ears_simple_and_convex(stdout["ears"])
    assert_ears_no_obstacle_intersection(stdout["ears"], stdout["obstacles"])
    job_convex = Job(id=Identifier("tri-c"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION, stdin=dict(TRIANGLE_STDIN), stdout=dict(stdout))
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())

    assert_convex_components_simple_convex_no_obstacle_intersection(
        stdout["convex_components"], stdout["obstacles"]
    )
    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    job_guard = Job(id=Identifier("tri-g"), step_name=StepName.GUARD_PLACEMENT, stdin=dict(TRIANGLE_STDIN), stdout=dict(stdout))
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert len(guard_out["guards"]) == 4, f"Triangle gallery expects 4 guards; got {len(guard_out['guards'])}"
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    assert "exclusivity" in guard_out, "Guard placement must return exclusivity"
    assert len(guard_out["exclusivity"]) == len(guard_out["guards"]), (
        f"exclusivity must have one entry per guard; got {len(guard_out['exclusivity'])} for {len(guard_out['guards'])} guards"
    )
    for guard_id, points in guard_out["exclusivity"].items():
        assert isinstance(points, list), f"exclusivity[{guard_id!r}] must be a list of points"
        assert len(points) >= 1, f"each guard must have at least one exclusivity point; guard {guard_id!r} has {len(points)}"
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Triangle guard coverage report")
