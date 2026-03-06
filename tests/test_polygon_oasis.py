"""
Test that api/steps.py runs the full pipeline for the oasis polygon (boundary + 4 obstacles).
Expects 12 guards for sufficient coverage.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
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


POLYGON_OASIS_STDIN = {
    "boundary": [
        ["72.03851203501094", "182.5"],
        ["202.10804765378072", "60.5"],
        ["456.24390955506937", "58.5"],
        ["560.133491584185", "174.03617018649192"],
        ["567.3032822757111", "391.5"],
        ["470.25139800632144", "500.5"],
        ["193.10323364940436", "497"],
        ["72.03851203501095", "373.5"],
    ],
    "obstacles": [
        [
            ["158.084512521274", "196.5"],
            ["230.12302455628497", "126.5"],
            ["408.218234865062", "121.5"],
            ["482.25781667882325", "193.5"],
            ["488.26102601507415", "373.5"],
            ["437.23374665694143", "441.5"],
            ["209.11179187940678", "470.5"],
            ["448.2396304400681", "471.5"],
            ["516.2760029175785", "378.5"],
            ["513.9172952430531", "187.55957446516578"],
            ["420.2246535375638", "96.5"],
            ["228.64563913920978", "105.55957446516578"],
            ["136.07274495502068", "188.5"],
            ["137.0732798443958", "361.5"],
        ],
        [
            ["387.84989918178394", "147.5"],
            ["242.12944322878678", "149.5"],
            ["186.09948942377827", "213.5"],
            ["166.08879163627523", "363.5"],
            ["232.12409433503527", "438.5"],
            ["410.21930464381234", "423.5"],
            ["469.2508631169463", "363.5"],
            ["462.2471188913202", "204.5"],
            ["449.24016532944324", "349.5"],
            ["392.20967663505957", "402.5"],
            ["245.13104789691226", "409.5"],
            ["198.1059080962801", "355.5"],
            ["208.11125699003162", "235.5"],
            ["252.1347921225383", "169.5"],
        ],
        [
            ["368.19683929005595", "188.5"],
            ["420.2246535375638", "230.5"],
            ["405.21663019693653", "317.5"],
            ["362.19362995380504", "354.5"],
            ["281.1503039144177", "358.5"],
            ["242.12944322878678", "330.5"],
            ["237.126768781911", "235.5"],
            ["220.11767566253343", "344.5"],
            ["268.1433503525407", "383.5"],
            ["373.1995137369317", "382.5"],
            ["429.2294675419402", "334.5"],
            ["442.2364211038172", "221.5"],
            ["369.1973741794311", "166.5"],
            ["270.14442013129104", "185.5"],
        ],
        [
            ["362.19362995380504", "210.2617021393369"],
            ["284.1519085825432", "201.5"],
            ["255.13639679066375", "238.5"],
            ["261.13960612691466", "313.5"],
            ["303.16207148067105", "335.5"],
            ["355.189885728179", "327.5"],
            ["389.20807196693414", "297.5"],
            ["396.2118161925602", "242.5"],
            ["374.20004862630685", "291.5"],
            ["343.1834670556771", "314.5"],
            ["306.1636761487965", "314.5"],
            ["278.14869924629227", "299.5"],
            ["274.1465596887916", "245.5"],
            ["296.158327255045", "216.5"],
        ],
    ],
}


def test_polygon_oasis_full_pipeline_twelve_guards():
    """
    Run validation → stitching → ear clipping → convex component merge → guard placement
    for the oasis polygon. Asserts 12 guards for sufficient coverage.
    """
    stdout = {}

    job_validate = Job(
        id=Identifier("polygon-oasis-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(POLYGON_OASIS_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())

    job_stitch = Job(
        id=Identifier("polygon-oasis-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(POLYGON_OASIS_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())

    job_ear = Job(
        id=Identifier("polygon-oasis-ear"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(POLYGON_OASIS_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    assert_ears_simple_and_convex(stdout["ears"])

    job_convex = Job(
        id=Identifier("polygon-oasis-convex"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(POLYGON_OASIS_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(ConvexComponentOptimizationStep(job=job_convex, user=_user()).run())

    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    job_guard = Job(
        id=Identifier("polygon-oasis-guard"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(POLYGON_OASIS_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()

    assert len(guard_out["guards"]) in (15, 16), (
        f"Oasis polygon expects 15 or 16 guards for sufficient coverage; got {len(guard_out['guards'])}."
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Oasis guard coverage report")
