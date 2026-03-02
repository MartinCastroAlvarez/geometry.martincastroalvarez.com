"""
Test that api/steps.py runs the full pipeline (validation, stitching, ear clipping,
convex component merge, guard placement) for the cross polygon job input.
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


# job.stdin from the cross polygon job (boundary + one obstacle)
CROSS_STDIN = {
    "boundary": [
        ["61.03262825188427", "222.5"],
        ["264.14121079504014", "206.5"],
        ["253.13532701191346", "20.5"],
        ["455.24337466569415", "23.5"],
        ["397.21235108193537", "208.5"],
        ["589.3150498419645", "186.5"],
        ["588.3145149525894", "352.5"],
        ["389.20807196693414", "316.5"],
        ["393.2102115244347", "483.5"],
        ["248.1326525650377", "476.5"],
        ["257.1374665694141", "332.5"],
        ["60.03209336250912", "334.5"],
    ],
    "obstacles": [
        [
            ["265.1417456844153", "273.5"],
            ["326.17437393629956", "331.5"],
            ["383.20486263068324", "263.5"],
            ["323.17276926817414", "210.5"],
        ],
    ],
}


def test_cross_full_pipeline_validation_stitching_ear_clipping_convex_guard_placement():
    """
    Run validation → stitching → ear clipping → convex component merge → guard placement
    for the cross polygon (api/steps.py). Asserts each step completes and final output
    has 4 guards and visibility.
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
    assert len(guard_out["guards"]) == 4, (
        f"Cross polygon expects 4 guards for sufficient coverage; got {len(guard_out['guards'])}"
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
