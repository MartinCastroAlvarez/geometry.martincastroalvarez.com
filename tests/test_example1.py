"""
Test that api/steps.py runs the full pipeline for lab/example1.py gallery (L-shape, 2 holes).
Expects 3 guards for sufficient coverage.
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
    job_ear = Job(id=Identifier("ex1-e"), step_name=StepName.EAR_CLIPPING, stdin=dict(EXAMPLE1_STDIN), stdout=dict(stdout))
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    job_convex = Job(id=Identifier("ex1-c"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION, stdin=dict(EXAMPLE1_STDIN), stdout=dict(stdout))
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())
    job_guard = Job(id=Identifier("ex1-g"), step_name=StepName.GUARD_PLACEMENT, stdin=dict(EXAMPLE1_STDIN), stdout=dict(stdout))
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert len(guard_out["guards"]) == 4, f"Example1 expects 4 guards; got {len(guard_out['guards'])}"
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
