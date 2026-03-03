"""
Test that api/steps.py runs the full pipeline for lab/example9.py gallery (serrated polygon, no holes).
Expects 4 guards for sufficient coverage.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from models import Job
from models import User
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


# Lab example9: serrated polygon. API requires boundary CCW; lab order is CW so we reverse.
EXAMPLE9_STDIN = {
    "boundary": [
        ["11.0", "0.0"],
        ["10.0", "10.0"],
        ["9.0", "2.0"],
        ["8.0", "2.0"],
        ["7.0", "10.0"],
        ["6.0", "2.0"],
        ["5.0", "2.0"],
        ["4.0", "10.0"],
        ["3.0", "2.0"],
        ["2.0", "2.0"],
        ["1.0", "10.0"],
        ["0.0", "0.0"],
    ],
    "obstacles": [],
}


def test_example9_full_pipeline_requires_four_guards():
    stdout = {}
    job_validate = Job(id=Identifier("ex9-v"), step_name=StepName.VALIDATE_POLYGONS, stdin=dict(EXAMPLE9_STDIN))
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(id=Identifier("ex9-s"), step_name=StepName.STITCHING, stdin=dict(EXAMPLE9_STDIN), stdout=dict(stdout))
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    job_ear = Job(id=Identifier("ex9-e"), step_name=StepName.EAR_CLIPPING, stdin=dict(EXAMPLE9_STDIN), stdout=dict(stdout))
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    job_convex = Job(id=Identifier("ex9-c"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION, stdin=dict(EXAMPLE9_STDIN), stdout=dict(stdout))
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())
    job_guard = Job(id=Identifier("ex9-g"), step_name=StepName.GUARD_PLACEMENT, stdin=dict(EXAMPLE9_STDIN), stdout=dict(stdout))
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert len(guard_out["guards"]) == 4, (
        f"Example9 polygon expects 4 guards for sufficient coverage; got {len(guard_out['guards'])}. "
        f"The guards are: {guard_out['guards']}. "
        f"The visibility is: {guard_out['visibility']}. "
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
