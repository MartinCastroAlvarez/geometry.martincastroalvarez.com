"""
Test that api/steps.py runs the full pipeline (validation, stitching, ear clipping,
convex component merge, guard placement) for the batman polygon job input.
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


# job.stdin from the batman polygon job (boundary with string coords, empty obstacles)
BATMAN_STDIN = {
    "boundary": [
        ["316.169025042548", "423.5"],
        ["142.0759542912716", "408.5"],
        ["100.0534889375152", "344.5"],
        ["88.04707026501337", "278.5"],
        ["88.04707026501337", "172.5"],
        ["121.06472161439339", "60.5"],
        ["139.07434962314613", "17.5"],
        ["212.11339654753223", "17.5"],
        ["316.169025042548", "18.5"],
        ["451.24123510819356", "30.5"],
        ["529.2829564794554", "87.5"],
        ["546.292049598833", "201.5"],
        ["526.28135181133", "291.5"],
        ["480.256746900073", "205.5"],
        ["434.23214198881595", "133.5"],
        ["312.16688548504743", "103.5"],
        ["270.14442013129104", "108.5"],
        ["287.15351325066865", "144.5"],
        ["324.17330415754924", "187.5"],
        ["376.2011184050572", "190.5"],
        ["420.2246535375638", "181.5"],
        ["437.23374665694143", "234.5"],
        ["405.21663019693653", "287.5"],
        ["325.1738390469244", "304.5"],
        ["262.1401410162898", "300.5"],
        ["249.13318745441285", "277.5"],
        ["297.15886214442014", "258.5"],
        ["296.158327255045", "224.5"],
        ["264.14121079504014", "198.5"],
        ["227.1214198881595", "167.5"],
        ["179.0957451981522", "165.5"],
        ["145.07755895939704", "182.5"],
        ["168.08986141502552", "258.5"],
        ["183.0978847556528", "315.5"],
        ["228.12195477753465", "347.5"],
        ["287.15351325066865", "375.5"],
        ["356.19042061755414", "396.5"],
        ["407.21769997568686", "397.5"],
    ],
    "obstacles": [],
}


def test_batman_full_pipeline_validation_stitching_ear_clipping_convex_guard_placement():
    """
    Run validation → stitching → ear clipping → convex component merge → guard placement
    for the batman polygon (api/steps.py). Asserts each step completes and final output
    has guards and visibility.
    """
    stdout = {}

    # 1. Validation
    job_validate = Job(
        id=Identifier("batman-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(BATMAN_STDIN),
    )
    validation_out = ValidationPolygonStep(job=job_validate, user=_user(), state={}).run()
    assert "boundary" in validation_out
    assert "obstacles" in validation_out
    stdout.update(validation_out)

    # 2. Stitching (no obstacles: stitched = boundary)
    job_stitch = Job(
        id=Identifier("batman-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(BATMAN_STDIN),
        stdout=dict(stdout),
    )
    stitch_out = StitchingStep(job=job_stitch, user=_user(), state={}).run()
    assert "stitched" in stitch_out
    assert "stitches" in stitch_out
    stdout.update(stitch_out)

    # 3. Ear clipping
    job_ear = Job(
        id=Identifier("batman-ear"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(BATMAN_STDIN),
        stdout=dict(stdout),
    )
    ear_out = EarClippingStep(job=job_ear, user=_user(), state={}).run()
    assert "ears" in ear_out
    stdout.update(ear_out)
    assert_ears_simple_and_convex(stdout["ears"])

    # 4. Convex component optimization
    job_convex = Job(
        id=Identifier("batman-convex"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(BATMAN_STDIN),
        stdout=dict(stdout),
    )
    convex_out = ConvexComponentOptimizationStep(job=job_convex, user=_user(), state={}).run()
    assert "convex_components" in convex_out
    assert "adjacency" in convex_out
    stdout.update(convex_out)

    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    # 5. Guard placement
    job_guard = Job(
        id=Identifier("batman-guard"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(BATMAN_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user(), state={}).run()
    assert "guards" in guard_out
    assert "visibility" in guard_out
    assert len(guard_out["guards"]) in (5, 4), (
        f"Batman polygon expects 5 or 4 guards for sufficient coverage; got {len(guard_out['guards'])}"
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Batman guard coverage report")
