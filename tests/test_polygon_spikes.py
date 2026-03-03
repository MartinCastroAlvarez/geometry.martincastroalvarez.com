"""
Test that api/steps.py runs the full pipeline (validation, stitching, ear clipping,
convex component merge, guard placement) for the spikes polygon job input.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import Ear
from geometry import Point
from models import Job
from models import User
from steps import ConvexComponentOptimizationStep
from steps import EarClippingStep
from steps import GuardPlacementStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


# job.stdin from the spikes polygon job (boundary with string coords, empty obstacles)
SPIKES_STDIN = {
    "boundary": [
        ["54.02888402625821", "438.5"],
        ["106.05669827376612", "41.5"],
        ["151.08076829564794", "344.5"],
        ["185.09895453440313", "346.5"],
        ["218.11660588378314", "35.5"],
        ["268.1433503525407", "343.5"],
        ["305.16314125942137", "344.5"],
        ["331.1770483831753", "29.5"],
        ["381.2037928519329", "340.5"],
        ["422.22572331631414", "337.5"],
        ["438.2342815463166", "32.5"],
        ["507.2711889132021", "343.5"],
        ["533.285096036956", "342.5"],
        ["556.2973984925845", "30.5"],
        ["618.3305616338439", "433.5"],
    ],
    "obstacles": [],
}


def test_spikes_full_pipeline_validation_stitching_ear_clipping_convex_guard_placement():
    """
    Run validation → stitching → ear clipping → convex component merge → guard placement
    for the spikes polygon (api/steps.py). Asserts each step completes and final output
    has 5 guards and visibility.
    """
    stdout = {}

    # 1. Validation
    job_validate = Job(
        id=Identifier("spikes-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(SPIKES_STDIN),
    )
    validation_out = ValidationPolygonStep(job=job_validate, user=_user()).run()
    assert "boundary" in validation_out
    assert "obstacles" in validation_out
    stdout.update(validation_out)

    # 2. Stitching (no obstacles: stitched = boundary)
    job_stitch = Job(
        id=Identifier("spikes-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(SPIKES_STDIN),
        stdout=dict(stdout),
    )
    stitch_out = StitchingStep(job=job_stitch, user=_user()).run()
    assert "stitched" in stitch_out
    assert "stitches" in stitch_out
    stdout.update(stitch_out)

    # 3. Ear clipping
    job_ear = Job(
        id=Identifier("spikes-ear"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(SPIKES_STDIN),
        stdout=dict(stdout),
    )
    ear_out = EarClippingStep(job=job_ear, user=_user()).run()
    assert "ears" in ear_out
    stdout.update(ear_out)
    for ear_id, ear_serialized in stdout["ears"].items():
        ear = Ear.unserialize(ear_serialized)
        assert ear.is_convex(), (
            f"Ear {ear_id} must be convex; got ear={ear_serialized}"
        )
        assert ear.is_simple(), (
            f"Ear {ear_id} must be simple; got ear={ear_serialized}"
        )
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
        id=Identifier("spikes-convex"),
        step_name=StepName.CONVEX_COMPONENT_OPTIMIZATION,
        stdin=dict(SPIKES_STDIN),
        stdout=dict(stdout),
    )
    convex_out = ConvexComponentOptimizationStep(job=job_convex, user=_user()).run()
    assert "convex_components" in convex_out
    assert "adjacency" in convex_out
    stdout.update(convex_out)

    # 5. Guard placement
    job_guard = Job(
        id=Identifier("spikes-guard"),
        step_name=StepName.GUARD_PLACEMENT,
        stdin=dict(SPIKES_STDIN),
        stdout=dict(stdout),
    )
    guard_out = GuardPlacementStep(job=job_guard, user=_user()).run()
    assert "guards" in guard_out
    assert "visibility" in guard_out
    assert len(guard_out["guards"]) == 5, (
        f"Spikes polygon expects 5 guards for sufficient coverage; got {len(guard_out['guards'])}"
    )
    assert len(guard_out["visibility"]) == len(guard_out["guards"])
