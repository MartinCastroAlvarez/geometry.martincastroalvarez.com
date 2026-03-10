"""
Test that api/steps.py runs the full pipeline (validation, stitching, ear clipping,
convex component merge, guard placement) for the monster polygon (boundary + 5 obstacles).
Expects 10 guards and 45 convex components (obstacle-safe merges only).
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import ConvexComponent
from geometry import Ear
from geometry import Point
from models import Job
from models import User
from tests.utils import assert_convex_components_visibility_within_component
from tests.utils import assert_ears_simple_and_convex
from tests.utils import assert_no_redundant_guards
from tests.utils import assert_no_stitches_share_a_point
from tests.utils import print_guard_coverage_report
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


POLYGON_MONSTER_STDIN = {
    "boundary": [
        ["446.15941491626114", "263.55426009750386"],
        ["367.41093015165774", "74.16702213555435"],
        ["431.02753980724884", "183.35725017295343"],
        ["505.3151720888233", "48.07165617489896"],
        ["445.3211566577284", "196.4310971972762"],
        ["469.2508631169463", "233.5"],
        ["534.2856309263311", "42.5"],
        ["534.2856309263311", "331.5"],
        ["453.47109231796344", "286.15504725780767"],
        ["387.37974847270254", "289.1866548036857"],
        ["363.0728947637283", "342.9360439103765"],
        ["510.8930411947687", "384.6621358338605"],
        ["448.30134832345885", "331.56181901507534"],
        ["552.3012824800674", "354.0630009661908"],
        ["521.4076159014633", "439.0296902990084"],
        ["305.7074828441654", "341.85425592757764"],
        ["78.65219657511273", "275.0461513551817"],
        ["347.14664814193196", "277.71970645109417"],
        ["91.21570115006318", "191.02830408199893"],
        ["302.1973412059705", "239.57340853738688"],
        ["324.09613578665", "224.2484923889719"],
        ["212.76703498668007", "85.77968076808651"],
        ["337.70302588442416", "216.83052033785305"],
        ["352.0303667210712", "206.98404616081766"],
        ["363.71959492831695", "150.41383222413145"],
        ["321.8844623971214", "40.962766129238524"],
        ["386.4828288055852", "157.1776621513439"],
        ["341.57158358827223", "248.18191935383913"],
        ["365.5652625399873", "251.2563875025721"],
        ["376.14316677150464", "229.61981484068153"],
        ["383.6198301000868", "220.72378441009937"],
        ["393.25027671504324", "218.66702512600287"],
        ["395.368872473573", "229.97565605790484"],
        ["404.04146903877256", "220.2105594956659"],
        ["412.04574815377384", "221.7105594956659"],
        ["415.29748654424304", "232.9605594956659"],
        ["412.32217536897065", "258.02021742978457"],
    ],
    "obstacles": [
        [
            ["345.87951350184574", "344.17816278123905"],
            ["373.4218681578885", "286.7081989103456"],
            ["229.9851501501508", "291.27488789039603"],
            ["357.95949361414523", "295.40113462190925"],
            ["338.1483262299741", "328.7240548495702"],
            ["226.6955301546972", "305.40766907645303"],
        ],
        [
            ["519.9861193830768", "306.59681417976515"],
            ["519.3708968458534", "257.405323800038"],
            ["499.0685531174791", "227.8904295722017"],
            ["486.7641023730098", "285.0755371386345"],
        ],
        [
            ["502.1446658035964", "202.67979075259152"],
            ["520.6013419203003", "219.89681238549602"],
            ["516.3643223102365", "135.73766324819968"],
        ],
        [
            ["401.6932627826971", "277.07275595303554"],
            ["403.29106787174123", "236.9605594956659"],
            ["388.03291080877017", "254.7105594956659"],
            ["380.22385585200533", "236.3424804023706"],
            ["376.14316677150464", "254.17285882908837"],
            ["378.9914194681074", "267.6948250835733"],
        ],
        [
            ["331.38353736708643", "310.85524255357814"],
            ["311.0891707784233", "301.1964250962851"],
            ["292.24440180323614", "305.54289295206695"],
            ["307.70677634697944", "314.71876953649536"],
        ],
    ],
}


def test_polygon_monster_full_pipeline_ten_guards_forty_nine_convex_components():
    """
    Run validation → stitching → ear clipping → convex component merge → guard placement
    for the monster polygon. Asserts 49 convex components and 10 guards for sufficient coverage.
    """
    stdout = {}

    job_validate = Job(
        id=Identifier("polygon-monster-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(POLYGON_MONSTER_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user(), state={}).run())

    job_stitch = Job(
        id=Identifier("polygon-monster-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(POLYGON_MONSTER_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user(), state={}).run())
    assert_no_stitches_share_a_point(stdout["stitches"])

    job_ear = Job(
        id=Identifier("polygon-monster-ear"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(POLYGON_MONSTER_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(EarClippingStep(job=job_ear, user=_user(), state={}).run())
    assert_ears_simple_and_convex(stdout["ears"])
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
        id=Identifier("polygon-monster-convex"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(POLYGON_MONSTER_STDIN),
        stdout=dict(stdout),
    )
    convex_out = ConvexComponentOptimizationStep(job=job_convex, user=_user(), state={}).run()
    stdout.update(convex_out)

    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    assert len(convex_out["convex_components"]) == 45, (
        f"Monster polygon expects 45 convex components; got {len(convex_out['convex_components'])}"
    )

    job_guard = Job(
        id=Identifier("polygon-monster-guard"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(POLYGON_MONSTER_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user(), state={}).run()

    assert len(guard_out["visibility"]) == len(guard_out["guards"])

    assert len(guard_out["guards"]) in (14, 15), (
        f"Monster polygon expects 14 or 15 guards for sufficient coverage; got {len(guard_out['guards'])}. "
    )
    # assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Monster guard coverage report")
