"""
Test that api/steps.py runs the full pipeline (validation, stitching, ear clipping,
convex component merge, guard placement) for the snake polygon job input.
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


# job.stdin from the snake polygon job (boundary with string coords, empty obstacles)
SNAKE_STDIN = {
    "boundary": [
        ["126.06739606126915", "483.5"],
        ["12.00641867250183", "197.5"],
        ["265.1417456844153", "326.5"],
        ["215.11500121565768", "32.5"],
        ["437.23374665694143", "229.5"],
        ["454.242839776319", "39.5"],
        ["624.3337709700949", "103.5"],
        ["502.2685144663263", "117.5"],
        ["510.2727935813275", "352.5"],
        ["323.1727692681741", "214.5"],
        ["333.1781181619256", "453.5"],
        ["126.06739606126915", "339.5"],
    ],
    "obstacles": [],
}


def test_snake_full_pipeline_validation_stitching_ear_clipping_convex_guard_placement():
    """
    Run validation → stitching → ear clipping → convex component merge → guard placement
    for the snake polygon (api/steps.py). Asserts each step completes and final output
    has guards and visibility.
    """
    stdout = {}

    # 1. Validation
    job_validate = Job(
        id=Identifier("snake-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(SNAKE_STDIN),
    )
    validation_out = ValidationPolygonStep(job=job_validate, user=_user()).run()
    assert "boundary" in validation_out
    assert "obstacles" in validation_out
    stdout.update(validation_out)

    # 2. Stitching (no obstacles: stitched = boundary)
    job_stitch = Job(
        id=Identifier("snake-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(SNAKE_STDIN),
        stdout=dict(stdout),
    )
    stitch_out = StitchingStep(job=job_stitch, user=_user()).run()
    assert "stitched" in stitch_out
    assert "stitches" in stitch_out
    stdout.update(stitch_out)

    # 3. Ear clipping
    job_ear = Job(
        id=Identifier("snake-ear"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(SNAKE_STDIN),
        stdout=dict(stdout),
    )
    ear_out = EarClippingStep(job=job_ear, user=_user()).run()
    assert "ears" in ear_out
    stdout.update(ear_out)
    assert_ears_simple_and_convex(stdout["ears"])

    # 4. Convex component optimization
    job_convex = Job(
        id=Identifier("snake-convex"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(SNAKE_STDIN),
        stdout=dict(stdout),
    )
    convex_out = ConvexComponentOptimizationStep(job=job_convex, user=_user()).run()
    assert "convex_components" in convex_out
    assert "adjacency" in convex_out
    stdout.update(convex_out)

    assert_convex_components_visibility_within_component(
        stdout["convex_components"], stdout["obstacles"]
    )

    # 5. Guard placement
    job_guard = Job(
        id=Identifier("snake-guard"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(SNAKE_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert "guards" in guard_out
    assert "visibility" in guard_out
    assert len(guard_out["guards"]) == 3, (
        f"Snake polygon expects 3 guards for sufficient coverage; got {len(guard_out['guards'])}"
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
    assert_no_redundant_guards(guard_out)
    print_guard_coverage_report(guard_out, "Snake guard coverage report")
