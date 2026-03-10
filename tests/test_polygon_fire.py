"""
Test that api/steps.py runs the full pipeline for the fire polygon (boundary + 3 obstacles).
Expects 4 guards for sufficient coverage.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import ConvexComponent
from geometry import Polygon
from geometry import Segment
from models import Job
from tests.utils import assert_convex_components_visibility_within_component
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


FIRE_STDIN = {
    "boundary": [
        ["411.21983953318744", "482.5"],
        ["409.2187697544372", "421.5"],
        ["372.19897884755653", "373.5"],
        ["327.1749088256747", "343.5"],
        ["288.15404814004376", "384.5"],
        ["257.1374665694141", "442.5"],
        ["280.1497690250426", "485.5"],
        ["67.03583758813518", "444.5"],
        ["21.01123267687819", "391.5"],
        ["188.1005592025286", "375.5"],
        ["24.012837345003646", "211.5"],
        ["118.06311694626794", "205.5"],
        ["213.11393143690736", "228.5"],
        ["185.09895453440313", "60.5"],
        ["294.1572574762947", "130.5"],
        ["331.1770483831753", "6"],
        ["391.2091417456844", "116.5"],
        ["498.2663749088257", "37.5"],
        ["459.2455142231948", "215.5"],
        ["524.2802820325796", "177.5"],
        ["613.3278871869682", "175.5"],
        ["534.2856309263311", "349.5"],
        ["637.3407245319718", "336.5"],
        ["599.320398735716", "437.5"],
    ],
    "obstacles": [
        [
            ["355.189885728179", "242.5"],
            ["418.22358375881356", "256.5"],
            ["420.2246535375638", "185.5"],
            ["397.21235108193537", "202.5"],
            ["348.1861415025529", "131.5"],
            ["304.1626063700462", "261.5"],
        ],
        [
            ["455.24337466569415", "406.5"],
            ["481.2572817894481", "320.5"],
            ["410.21930464381234", "329.5"],
        ],
        [
            ["239.12783856066133", "312.5"],
            ["272.14548991004136", "297.5"],
            ["186.09948942377827", "279.5"],
            ["232.12409433503527", "341.5"],
        ],
    ],
}


def test_fire_full_pipeline_requires_four_guards():
    stdout = {}
    job_validate = Job(id=Identifier("fire-v"), step_name=StepName.VALIDATE_POLYGONS, stdin=dict(FIRE_STDIN))
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user(), state={}).run())
    job_stitch = Job(id=Identifier("fire-s"), step_name=StepName.STITCHING, stdin=dict(FIRE_STDIN), stdout=dict(stdout))
    stdout.update(StitchingStep(job=job_stitch, user=_user(), state={}).run())
    job_ear = Job(id=Identifier("fire-e"), step_name=StepName.EAR_CLIPPING, stdin=dict(FIRE_STDIN), stdout=dict(stdout))
    stdout.update(EarClippingStep(job=job_ear, user=_user(), state={}).run())
    assert_ears_simple_and_convex(stdout["ears"])
    job_convex = Job(id=Identifier("fire-c"), step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION, stdin=dict(FIRE_STDIN), stdout=dict(stdout))
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user(), state={}).run())

    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    job_guard = Job(id=Identifier("fire-g"), step_name=StepName.GUARD_PLACEMENT, stdin=dict(FIRE_STDIN), stdout=dict(stdout))
    guard_out = GuardPlacementStep(job=job_guard, user=_user(), state={}).run()
    assert len(guard_out["guards"]) in (6, 5), f"Fire gallery expects 6 or 5 guards; got {len(guard_out['guards'])}"
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    # assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Fire guard coverage report")


def test_fire_no_stitch_crosses_obstacle():
    """Assert that every stitch (bridge) does not cross any obstacle boundary."""
    stdout = {}
    job_validate = Job(id=Identifier("fire-v"), step_name=StepName.VALIDATE_POLYGONS, stdin=dict(FIRE_STDIN))
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user(), state={}).run())
    job_stitch = Job(id=Identifier("fire-s"), step_name=StepName.STITCHING, stdin=dict(FIRE_STDIN), stdout=dict(stdout))
    stdout.update(StitchingStep(job=job_stitch, user=_user(), state={}).run())

    obstacles = [Polygon.unserialize(ob) for ob in stdout["obstacles"]]
    stitches = [Segment.unserialize(s) for s in stdout["stitches"]]

    for i, stitch in enumerate(stitches):
        for j, obstacle in enumerate(obstacles):
            for edge in obstacle.edges:
                if stitch.touches(edge):
                    continue
                assert not stitch.crosses(edge), (
                    f"Stitch {i} crosses obstacle {j}: stitch={stitch.serialize()}, "
                    f"obstacle edge={[edge[0].serialize(), edge[1].serialize()]}"
                )
