"""
Test that api/steps.py runs the full pipeline for the sky polygon (boundary + obstacles).
Expects 12 guards for sufficient coverage.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from exceptions import SuspendedStepError
from geometry import ConvexComponent
from geometry import Ear
from geometry import Polygon
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


POLYGON_SKY_STDIN = {
    "boundary": [
        ["39.02086068563093", "383.5"],
        ["36.01925601750547", "136.5"],
        ["101.05402382689036", "35.5"],
        ["405.21663019693653", "32.5"],
        ["401.21449063943595", "155.5"],
        ["483.2583515681984", "33.5"],
        ["486.2599562363239", "258.5"],
        ["469.2508631169463", "258.5"],
        ["482.25781667882325", "305.5"],
        ["415.2219790906881", "319.5"],
        ["481.2572817894481", "329.5"],
        ["472.25246778507176", "380.5"],
        ["517.2765378069536", "380.5"],
        ["496.2653051300754", "331.5"],
        ["566.302747386336", "318.5"],
        ["500.26744468757596", "303.5"],
        ["501.2679795769511", "259.5"],
        ["500.267444687576", "37.5"],
        ["542.2899100413323", "37.5"],
        ["541.2893751519573", "117.5"],
        ["614.3284220763434", "116.5"],
        ["614.3284220763434", "188.5"],
        ["541.2893751519573", "185.5"],
        ["543.2904449307075", "281.5"],
        ["618.3305616338439", "283.5"],
        ["615.3289569657185", "386.5"],
        ["537.2872355944565", "346.5"],
        ["552.2952589350839", "475.5"],
        ["444.2374908825675", "472.5"],
        ["453.2423048869439", "341.5"],
        ["377.20165329443233", "405.5"],
        ["376.2011184050572", "324.5"],
        ["345.18453683442743", "291.5"],
        ["298.1593970337953", "292.5"],
        ["262.1401410162898", "327.5"],
        ["256.1369316800389", "361.5"],
        ["299.15993192317046", "360.5"],
        ["328.1754437150499", "411.5"],
        ["327.1749088256747", "477.5"],
        ["82.04386092876246", "480.5"],
    ],
    "obstacles": [
        [
            ["377.20165329443233", "257.5"],
            ["377.20165329443233", "178.5"],
            ["266.14228057379046", "180.5"],
            ["264.14121079504014", "253.5"],
        ],
        [
            ["110.05883783126671", "149.5"],
            ["207.11072210065646", "146.5"],
            ["206.1101872112813", "64.5"],
            ["113.06044249939218", "64.5"],
        ],
        [
            ["267.14281546316556", "148.5"],
            ["377.20165329443233", "148.5"],
            ["378.20218818380744", "119.5"],
            ["297.15886214442014", "120.5"],
            ["298.1593970337953", "93.5"],
            ["378.20218818380744", "92.5"],
            ["378.20218818380744", "64.5"],
            ["265.1417456844153", "64.5"],
        ],
        [
            ["106.05669827376612", "417.5"],
            ["209.11179187940678", "418.5"],
            ["208.11125699003162", "377.5"],
            ["166.08879163627523", "374.5"],
            ["162.08665207877462", "324.5"],
            ["110.05883783126671", "323.5"],
        ],
        [
            ["109.05830294189157", "275.5"],
            ["209.11179187940678", "276.5"],
            ["211.11286165815707", "180.5"],
            ["107.05723316314126", "179.5"],
            ["111.05937272064187", "207.5"],
            ["187.10002431315343", "209.5"],
            ["190.10162898127885", "241.5"],
            ["109.05830294189158", "246.5"],
        ],
    ],
}


def test_sky_full_pipeline_requires_twelve_guards():
    stdout = {}
    job_validate = Job(
        id=Identifier("sky-v"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(POLYGON_SKY_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user(), state={}).run())
    job_stitch = Job(
        id=Identifier("sky-s"),
        step_name=StepName.STITCHING,
        stdin=dict(POLYGON_SKY_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user(), state={}).run())
    assert_no_stitches_share_a_point(stdout["stitches"])
    job_ear = Job(
        id=Identifier("sky-e"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(POLYGON_SKY_STDIN),
        stdout=dict(stdout),
    )
    state = {}
    while True:
        step = EarClippingStep(job=job_ear, user=_user(), state=state)
        try:
            stdout.update(step.run())
            break
        except SuspendedStepError as e:
            state = e.state
    assert_ears_simple_and_convex(stdout["ears"])

    stitched_points = set(Polygon.unserialize(stdout["stitched"]))
    ears_points = set()
    for ear_ser in stdout["ears"].values():
        ear = Ear.unserialize(ear_ser)
        ears_points.update(ear)
    assert stitched_points == ears_points, (
        f"Ears' vertices must equal stitched vertices. "
        f"Only in stitched: {stitched_points - ears_points}. "
        f"Only in ears: {ears_points - stitched_points}."
    )

    job_convex = Job(
        id=Identifier("sky-c"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(POLYGON_SKY_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user(), state={}).run())

    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    stitched_points = set(Polygon.unserialize(stdout["stitched"]))
    component_points = set()
    for comp_ser in stdout["convex_components"].values():
        comp = ConvexComponent.unserialize(comp_ser)
        component_points.update(comp)
    assert stitched_points == component_points, (
        f"Convex components' vertices must equal stitched vertices. "
        f"Only in stitched: {stitched_points - component_points}. "
        f"Only in components: {component_points - stitched_points}."
    )

    job_guard = Job(
        id=Identifier("sky-g"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(POLYGON_SKY_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user(), state={}).run()
    assert len(guard_out["guards"]) == 13, (
        f"Sky gallery expects 13 guards; got {len(guard_out['guards'])}"
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Sky guard coverage report")
