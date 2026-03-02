"""
Test that api/steps.py runs the full pipeline for lab/example5.py gallery (20 vertices, 3 valid holes).
Expects 5 guards for sufficient coverage.
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


EXAMPLE5_STDIN = {
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
        [["7.0", "19.0"], ["9.0", "19.0"], ["9.0", "15.0"], ["7.0", "15.0"]],
    ],
}


def test_example5_full_pipeline_requires_five_guards():
    stdout = {}
    job_validate = Job(id=Identifier("ex5-v"), step_name=StepName.VALIDATE_POLYGONS, stdin=dict(EXAMPLE5_STDIN))
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(id=Identifier("ex5-s"), step_name=StepName.STITCHING, stdin=dict(EXAMPLE5_STDIN), stdout=dict(stdout))
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    job_ear = Job(id=Identifier("ex5-e"), step_name=StepName.EAR_CLIPPING, stdin=dict(EXAMPLE5_STDIN), stdout=dict(stdout))
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    job_convex = Job(id=Identifier("ex5-c"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION, stdin=dict(EXAMPLE5_STDIN), stdout=dict(stdout))
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())
    job_guard = Job(id=Identifier("ex5-g"), step_name=StepName.GUARD_PLACEMENT, stdin=dict(EXAMPLE5_STDIN), stdout=dict(stdout))
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert len(guard_out["guards"]) == 5, f"Example5 expects 5 guards; got {len(guard_out['guards'])}"
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
