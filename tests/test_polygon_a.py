"""
Test that api/steps.py runs the full pipeline (validation, stitching, ear clipping,
convex component merge, guard placement) for polygon A (boundary + one obstacle).
Expects 2 guards for sufficient coverage. Asserts coverage (stitched + convex edge midpoints) in output.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import ConvexComponent
from geometry import Ear
from geometry import Point
from geometry import Polygon
from geometry import Segment
from geometry.polygon import _segments_share_endpoint
from models import Job
from models import User
from tests.utils import assert_convex_components_visibility_within_component
from tests.utils import assert_ears_simple_and_convex
from tests.utils import assert_no_redundant_guards
from tests.utils import print_guard_coverage_report
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


POLYGON_A_STDIN = {
    "boundary": [
        ["98.05241915876489", "488.5"],
        ["317.1695599319232", "12.5"],
        ["565.3022124969609", "487.5"],
        ["319.1706297106735", "329.5"],
    ],
    "obstacles": [
        [
            ["325.17383904692446", "251.5"],
            ["383.20486263068324", "272.5"],
            ["323.1727692681741", "145.5"],
            ["268.1433503525407", "277.5"],
        ],
    ],
}


def test_polygon_a_full_pipeline_requires_one_guard():
    """
    Run validation → stitching → ear clipping → convex component merge → guard placement
    for polygon A. Asserts 1 guard for sufficient coverage.
    """
    stdout = {}

    job_validate = Job(
        id=Identifier("polygon-a-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(POLYGON_A_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())

    job_stitch = Job(
        id=Identifier("polygon-a-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(POLYGON_A_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    assert len(stdout["stitches"]) == 1, (
        f"Polygon A stitching must produce 1 stitch; got {len(stdout['stitches'])}. "
        f"stitches={stdout['stitches']}"
    )

    job_ear = Job(
        id=Identifier("polygon-a-ear"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(POLYGON_A_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    assert_ears_simple_and_convex(stdout["ears"])
    for ear_id, ear_serialized in stdout["ears"].items():
        ear = Ear.unserialize(ear_serialized)
        assert ear.is_ccw(), (
            f"Ear {ear_id} must be counter-clockwise; got ear={ear_serialized}"
        )

    # No ear must overlap another: each ear's interior must not contain the centroid of any other ear.
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

    assert len(stdout["ears"]) == 8, (
        f"Polygon A ear clipping must produce 8 ears; got {len(stdout['ears'])}. "
        f"ears keys={list(stdout['ears'].keys())}"
    )

    job_convex = Job(
        id=Identifier("polygon-a-convex"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(POLYGON_A_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())

    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    job_guard = Job(
        id=Identifier("polygon-a-guard"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(POLYGON_A_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()

    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    assert "coverage" in guard_out, "Guard placement must return coverage (stitched points + convex edge midpoints)."
    assert isinstance(guard_out["coverage"], list), "coverage must be a list of points."
    assert len(guard_out["coverage"]) >= len(stdout["stitched"]), (
        "coverage must include at least all stitched vertices."
    )

    # Every segment from a guard to a point in its visibility must not intersect or go through any obstacle.
    obstacle_polygons = [Polygon.unserialize(obs) for obs in stdout["obstacles"]]
    for guard_id, guard_serialized in guard_out["guards"].items():
        guard = Point.unserialize(guard_serialized)
        visible_serialized = guard_out["visibility"].get(guard_id)
        assert visible_serialized is not None, f"No visibility for guard {guard_id}"
        for visible_ser in visible_serialized:
            visible_pt = Point.unserialize(visible_ser)
            segment = Segment([guard, visible_pt])
            for obstacle in obstacle_polygons:
                assert not obstacle.contains(segment.midpoint, inclusive=False), (
                    f"Segment from guard {guard} to visible point {visible_pt} goes through obstacle: "
                    f"midpoint {segment.midpoint} is inside obstacle."
                )
                for edge in obstacle.edges:
                    if _segments_share_endpoint(edge, segment):
                        continue
                    if segment.crosses(edge):
                        raise AssertionError(
                            f"Segment from guard {guard} to visible point {visible_pt} intersects obstacle edge "
                            f"{edge[0]}–{edge[1]}."
                        )

    assert len(guard_out["guards"]) == 2, (
        f"Polygon A expects 2 guards for sufficient coverage; got {len(guard_out['guards'])}. "
        f"The guards are: {guard_out['guards']}. "
        f"The visibility is: {guard_out['visibility']}. "
    )
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Polygon A guard coverage report")
