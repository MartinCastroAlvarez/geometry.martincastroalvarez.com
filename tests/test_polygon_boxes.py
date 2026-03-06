"""
Test that api/steps.py runs the full pipeline for the boxes polygon (boundary + 2 obstacles).
Expects 3 guards for sufficient coverage.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import Ear
from geometry import Point
from models import Job
from models import User
from tests.utils import assert_convex_components_simple_convex_no_obstacle_intersection
from tests.utils import assert_convex_components_visibility_within_component
from tests.utils import assert_ears_no_obstacle_intersection
from tests.utils import assert_ears_simple_and_convex
from tests.utils import print_guard_coverage_report
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


POLYGON_BOXES_STDIN = {
    "boundary": [
        ["82.04386092876247", "183.5"],
        ["259.1385363481644", "183.5"],
        ["260.1390712375395", "43.5"],
        ["455.24337466569415", "44.5"],
        ["451.24123510819356", "183.5"],
        ["602.671127079171", "187.35531948902567"],
        ["588.8807756992674", "352.5"],
        ["461.9576027961888", "348.5"],
        ["463.2476537806954", "496.5"],
        ["84.04493070751276", "491.5"],
    ],
    "obstacles": [
        [
            ["128.06846584001943", "448.5"],
            ["228.12195477753465", "452.5"],
            ["223.1192803306589", "357.5"],
            ["125.066861171894", "356.5"],
        ],
        [
            ["308.1647459275468", "150.5"],
            ["383.20486263068324", "159.5"],
            ["386.09789876313437", "78.53617012774359"],
            ["315.09611112939", "82.46382987225641"],
        ],
    ],
}


def test_polygon_boxes_full_pipeline_three_guards():
    """
    Run validation → stitching → ear clipping → convex component merge → guard placement
    for the boxes polygon. Asserts 3 guards for sufficient coverage.
    """
    stdout = {}

    job_validate = Job(
        id=Identifier("polygon-boxes-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(POLYGON_BOXES_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())

    job_stitch = Job(
        id=Identifier("polygon-boxes-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(POLYGON_BOXES_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())

    job_ear = Job(
        id=Identifier("polygon-boxes-ear"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(POLYGON_BOXES_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    assert_ears_simple_and_convex(stdout["ears"])
    assert_ears_no_obstacle_intersection(stdout["ears"], stdout["obstacles"])
    for ear_id, ear_serialized in stdout["ears"].items():
        ear = Ear.unserialize(ear_serialized)
        assert ear.is_ccw(), (
            f"Ear {ear_id} must be counter-clockwise; got ear={ear_serialized}"
        )
    ears_list = [Ear.unserialize(ser) for ser in stdout["ears"].values()]
    ear_ids = list(stdout["ears"].keys())
    for i, ear_a in enumerate(ears_list):
        centroid_a = Point([
            sum(p.x for p in ear_a) / len(ear_a),
            sum(p.y for p in ear_a) / len(ear_a),
        ])
        for j, ear_b in enumerate(ears_list):
            if i == j:
                continue
            centroid_b = Point([
                sum(p.x for p in ear_b) / len(ear_b),
                sum(p.y for p in ear_b) / len(ear_b),
            ])
            assert not ear_a.contains(centroid_b, inclusive=False), (
                f"Ear {ear_ids[i]} overlaps ear {ear_ids[j]}: ear {i} contains centroid of ear {j}."
            )
            assert not ear_b.contains(centroid_a, inclusive=False), (
                f"Ear {ear_ids[j]} overlaps ear {ear_ids[i]}: ear {j} contains centroid of ear {i}."
            )

    job_convex = Job(
        id=Identifier("polygon-boxes-convex"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(POLYGON_BOXES_STDIN),
        stdout=dict(stdout),
    )
    convex_out = ConvexComponentOptimizationStep(job=job_convex, user=_user()).run()
    stdout.update(convex_out)

    assert_convex_components_simple_convex_no_obstacle_intersection(
        stdout["convex_components"], stdout["obstacles"]
    )
    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    job_guard = Job(
        id=Identifier("polygon-boxes-guard"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(POLYGON_BOXES_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()

    assert len(guard_out["visibility"]) == len(guard_out["guards"])

    assert len(guard_out["guards"]) == 3, (
        f"Boxes polygon expects 3 guards for sufficient coverage; got {len(guard_out['guards'])}."
    )
    print_guard_coverage_report(guard_out, "Boxes guard coverage report")
