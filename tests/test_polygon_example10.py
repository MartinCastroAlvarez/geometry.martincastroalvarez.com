"""
Test that api/steps.py runs the full pipeline for lab/example10.py gallery (serrated polygon built in loop, no holes).
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


def _example10_polygon():
    """Build polygon as in lab/example10.py (loop). API requires CCW; lab order is CW so we reverse."""
    polygon = [["0.0", "0.0"], ["1.0", "10.0"], ["2.0", "2.0"]]
    for i in range(10):
        polygon.append([str(3 + 3 * i + 0), "2.0"])
        polygon.append([str(3 + 3 * i + 1), "10.0"])
        polygon.append([str(3 + 3 * i + 2), "2.0"])
    polygon.append([str(3 + 3 * 9 + 3), "2.0"])
    polygon.append([str(3 + 3 * 9 + 4), "10.0"])
    polygon.append([str(3 + 3 * 9 + 5), "0.0"])
    return list(reversed(polygon))


EXAMPLE10_STDIN = {"boundary": _example10_polygon(), "obstacles": []}


def test_example10_full_pipeline_requires_four_guards():
    stdout = {}
    job_validate = Job(id=Identifier("ex10-v"), step_name=StepName.VALIDATE_POLYGONS, stdin=dict(EXAMPLE10_STDIN))
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(id=Identifier("ex10-s"), step_name=StepName.STITCHING, stdin=dict(EXAMPLE10_STDIN), stdout=dict(stdout))
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    job_ear = Job(id=Identifier("ex10-e"), step_name=StepName.EAR_CLIPPING, stdin=dict(EXAMPLE10_STDIN), stdout=dict(stdout))
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    job_convex = Job(id=Identifier("ex10-c"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION, stdin=dict(EXAMPLE10_STDIN), stdout=dict(stdout))
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())
    job_guard = Job(id=Identifier("ex10-g"), step_name=StepName.GUARD_PLACEMENT, stdin=dict(EXAMPLE10_STDIN), stdout=dict(stdout))
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert len(guard_out["guards"]) == 4, f"Example10 expects 4 guards; got {len(guard_out['guards'])}"
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
