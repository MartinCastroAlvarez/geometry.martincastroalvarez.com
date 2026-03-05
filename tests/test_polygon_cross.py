"""
Test that api/steps.py runs the full pipeline (validation, stitching, ear clipping,
convex component merge, guard placement) for the cross polygon job input.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import ConvexComponent
from geometry import Ear
from geometry import Point
from geometry import Polygon
from geometry import Segment
from models import Job
from models import User
from tests.utils import assert_convex_components_simple_convex_no_obstacle_intersection
from tests.utils import assert_convex_components_visibility_within_component
from tests.utils import assert_ears_no_obstacle_intersection
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


# job.stdin from the cross polygon job (boundary + one obstacle)
CROSS_STDIN = {
    "boundary": [
        ["250.13372234378798", "157.5"],
        ["240.1283734500365", "3.5"],
        ["418.22358375881356", "1.5"],
        ["395.211281303185", "154.5"],
        ["568.3038171650863", "133.5"],
        ["568.3038171650863", "306.5"],
        ["410.21930464381234", "302.5"],
        ["449.24016532944324", "448.5"],
        ["242.12944322878678", "456.5"],
        ["253.13532701191346", "307.5"],
        ["71.0379771456358", "327.5"],
        ["75.0401167031364", "137.5"],
    ],
    "obstacles": [
        [
            ["404.21609530756143", "223.5"],
            ["323.1727692681741", "154.5"],
            ["246.1315827862874", "242.5"],
            ["331.1770483831753", "317.5"],
        ],
    ],
}


def test_cross_full_pipeline_validation_stitching_ear_clipping_convex_guard_placement():
    """
    Run validation → stitching → ear clipping → convex component merge → guard placement
    for the cross polygon (api/steps.py). Asserts each step completes and final output
    has 2 guards and visibility.
    """
    stdout = {}

    # 1. Validation
    job_validate = Job(
        id=Identifier("cross-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(CROSS_STDIN),
    )
    validation_out = ValidationPolygonStep(job=job_validate, user=_user()).run()
    assert "boundary" in validation_out
    assert "obstacles" in validation_out
    stdout.update(validation_out)

    # 2. Stitching (boundary + obstacles merged)
    job_stitch = Job(
        id=Identifier("cross-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(CROSS_STDIN),
        stdout=dict(stdout),
    )
    stitch_out = StitchingStep(job=job_stitch, user=_user()).run()
    assert "stitched" in stitch_out
    assert "stitches" in stitch_out
    stdout.update(stitch_out)

    # 3. Ear clipping
    job_ear = Job(
        id=Identifier("cross-ear"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(CROSS_STDIN),
        stdout=dict(stdout),
    )
    ear_out = EarClippingStep(job=job_ear, user=_user()).run()
    assert "ears" in ear_out
    stdout.update(ear_out)
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

    # 4. Convex component optimization
    job_convex = Job(
        id=Identifier("cross-convex"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(CROSS_STDIN),
        stdout=dict(stdout),
    )
    convex_out = ConvexComponentOptimizationStep(job=job_convex, user=_user()).run()
    assert "convex_components" in convex_out
    assert "adjacency" in convex_out
    stdout.update(convex_out)

    assert_convex_components_simple_convex_no_obstacle_intersection(
        stdout["convex_components"], stdout["obstacles"]
    )
    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    # 5. Guard placement
    job_guard = Job(
        id=Identifier("cross-guard"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(CROSS_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert "guards" in guard_out
    assert "visibility" in guard_out
    assert len(guard_out["visibility"]) == len(guard_out["guards"])

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
                    if edge.connects(segment):
                        continue
                    assert not segment.intersects(edge, inclusive=False), (
                        f"Segment from guard {guard} to visible point {visible_pt} intersects obstacle edge "
                        f"{edge[0]}–{edge[1]}."
                    )

    assert len(guard_out["guards"]) == 4, (
        f"Cross polygon expects 4 guards for sufficient coverage; got {len(guard_out['guards'])}"
    )
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Cross guard coverage report")
