"""
Test that api/steps.py runs the full pipeline for lab/example6.py gallery (100-gon, 10 holes).
Expects 6 guards for sufficient coverage.
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


# 100-gon approximating a circle + 10 rectangular holes (from lab/example6.py)
EXAMPLE6_BOUNDARY = [
    ["100.0", "50.0"], ["99.9", "53.1"], ["99.6", "56.3"], ["99.1", "59.4"], ["98.4", "62.4"],
    ["97.6", "65.5"], ["96.5", "68.4"], ["95.2", "71.3"], ["93.8", "74.1"], ["92.2", "76.8"],
    ["90.5", "79.4"], ["88.5", "81.9"], ["86.4", "84.2"], ["84.2", "86.4"], ["81.9", "88.5"],
    ["79.4", "90.5"], ["76.8", "92.2"], ["74.1", "93.8"], ["71.3", "95.2"], ["68.4", "96.5"],
    ["65.5", "97.6"], ["62.4", "98.4"], ["59.4", "99.1"], ["56.3", "99.6"], ["53.1", "99.9"],
    ["50.0", "100.0"], ["46.9", "99.9"], ["43.7", "99.6"], ["40.6", "99.1"], ["37.6", "98.4"],
    ["34.5", "97.6"], ["31.6", "96.5"], ["28.7", "95.2"], ["25.9", "93.8"], ["23.2", "92.2"],
    ["20.6", "90.5"], ["18.1", "88.5"], ["15.8", "86.4"], ["13.6", "84.2"], ["11.5", "81.9"],
    ["9.5", "79.4"], ["7.8", "76.8"], ["6.2", "74.1"], ["4.8", "71.3"], ["3.5", "68.4"],
    ["2.4", "65.5"], ["1.6", "62.4"], ["0.9", "59.4"], ["0.4", "56.3"], ["0.1", "53.1"],
    ["0.0", "50.0"], ["0.1", "46.9"], ["0.4", "43.7"], ["0.9", "40.6"], ["1.6", "37.6"],
    ["2.4", "34.5"], ["3.5", "31.6"], ["4.8", "28.7"], ["6.2", "25.9"], ["7.8", "23.2"],
    ["9.5", "20.6"], ["11.5", "18.1"], ["13.6", "15.8"], ["15.8", "13.6"], ["18.1", "11.5"],
    ["20.6", "9.5"], ["23.2", "7.8"], ["25.9", "6.2"], ["28.7", "4.8"], ["31.6", "3.5"],
    ["34.5", "2.4"], ["37.6", "1.6"], ["40.6", "0.9"], ["43.7", "0.4"], ["46.9", "0.1"],
    ["50.0", "0.0"], ["53.1", "0.1"], ["56.3", "0.4"], ["59.4", "0.9"], ["62.4", "1.6"],
    ["65.5", "2.4"], ["68.4", "3.5"], ["71.3", "4.8"], ["74.1", "6.2"], ["76.8", "7.8"],
    ["79.4", "9.5"], ["81.9", "11.5"], ["84.2", "13.6"], ["86.4", "15.8"], ["88.5", "18.1"],
    ["90.5", "20.6"], ["92.2", "23.2"], ["93.8", "25.9"], ["95.2", "28.7"], ["96.5", "31.6"],
    ["97.6", "34.5"], ["98.4", "37.6"], ["99.1", "40.6"], ["99.6", "43.7"], ["99.9", "46.9"],
]
EXAMPLE6_HOLES = [
    [["17.0", "17.0"], ["17.0", "23.0"], ["23.0", "23.0"], ["23.0", "17.0"]],
    [["32.0", "17.0"], ["32.0", "23.0"], ["38.0", "23.0"], ["38.0", "17.0"]],
    [["47.0", "17.0"], ["47.0", "23.0"], ["53.0", "23.0"], ["53.0", "17.0"]],
    [["62.0", "17.0"], ["62.0", "23.0"], ["68.0", "23.0"], ["68.0", "17.0"]],
    [["77.0", "17.0"], ["77.0", "23.0"], ["83.0", "23.0"], ["83.0", "17.0"]],
    [["17.0", "32.0"], ["17.0", "38.0"], ["23.0", "38.0"], ["23.0", "32.0"]],
    [["32.0", "32.0"], ["32.0", "38.0"], ["38.0", "38.0"], ["38.0", "32.0"]],
    [["47.0", "32.0"], ["47.0", "38.0"], ["53.0", "38.0"], ["53.0", "32.0"]],
    [["62.0", "32.0"], ["62.0", "38.0"], ["68.0", "38.0"], ["68.0", "32.0"]],
    [["77.0", "32.0"], ["77.0", "38.0"], ["83.0", "38.0"], ["83.0", "32.0"]],
]
EXAMPLE6_STDIN = {"boundary": EXAMPLE6_BOUNDARY, "obstacles": EXAMPLE6_HOLES}


def test_example6_full_pipeline_requires_six_guards():
    stdout = {}
    job_validate = Job(id=Identifier("ex6-v"), step_name=StepName.VALIDATE_POLYGONS, stdin=dict(EXAMPLE6_STDIN))
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(id=Identifier("ex6-s"), step_name=StepName.STITCHING, stdin=dict(EXAMPLE6_STDIN), stdout=dict(stdout))
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    job_ear = Job(id=Identifier("ex6-e"), step_name=StepName.EAR_CLIPPING, stdin=dict(EXAMPLE6_STDIN), stdout=dict(stdout))
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    job_convex = Job(id=Identifier("ex6-c"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION, stdin=dict(EXAMPLE6_STDIN), stdout=dict(stdout))
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())
    job_guard = Job(id=Identifier("ex6-g"), step_name=StepName.GUARD_PLACEMENT, stdin=dict(EXAMPLE6_STDIN), stdout=dict(stdout))
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert len(guard_out["guards"]) == 6, f"Example6 expects 6 guards; got {len(guard_out['guards'])}"
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
