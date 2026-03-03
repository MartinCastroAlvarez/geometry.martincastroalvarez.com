"""
Test that api/steps.py runs the full pipeline for the triangle gallery (boundary + 2 triangular obstacles).
Expects 2 guards for sufficient coverage.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import ConvexComponent
from models import Job
from models import User
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


TRIANGLE_STDIN = {
    "boundary": [
        ["210.1123267687819", "430.5"],
        ["208.34857717919652", "70.45523736025557"],
        ["638.8053392651282", "247.41063691215174"],
        ["351.27715649008496", "242.22765922803794"],
    ],
    "obstacles": [
        [
            ["375.98751265626265", "195.1276681609867"],
            ["249.38365467855346", "135.6255365917006"],
            ["259.93397617669586", "200.40000893294877"],
        ],
        [
            ["308.16401731106123", "231.2808620258694"],
            ["255.4124098203491", "230.52767048701767"],
            ["257.6731929985225", "298.3149089836727"],
        ],
    ],
}


def test_triangle_full_pipeline_requires_two_guards():
    stdout = {}
    job_validate = Job(id=Identifier("tri-v"), step_name=StepName.VALIDATE_POLYGONS, stdin=dict(TRIANGLE_STDIN))
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(id=Identifier("tri-s"), step_name=StepName.STITCHING, stdin=dict(TRIANGLE_STDIN), stdout=dict(stdout))
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    job_ear = Job(id=Identifier("tri-e"), step_name=StepName.EAR_CLIPPING, stdin=dict(TRIANGLE_STDIN), stdout=dict(stdout))
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    job_convex = Job(id=Identifier("tri-c"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION, stdin=dict(TRIANGLE_STDIN), stdout=dict(stdout))
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())

    # All convex components must be convex and simple.
    for comp_id, comp_serialized in stdout["convex_components"].items():
        component = ConvexComponent.unserialize(comp_serialized)
        assert component.is_convex(), (
            f"Convex component {comp_id} must be convex; got component={comp_serialized}"
        )
        assert component.is_simple(), (
            f"Convex component {comp_id} must be simple; got component={comp_serialized}"
        )

    job_guard = Job(id=Identifier("tri-g"), step_name=StepName.GUARD_PLACEMENT, stdin=dict(TRIANGLE_STDIN), stdout=dict(stdout))
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert len(guard_out["guards"]) == 2, f"Triangle gallery expects 2 guards; got {len(guard_out['guards'])}"
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
