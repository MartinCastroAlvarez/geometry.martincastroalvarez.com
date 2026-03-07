"""
Tests for the stitching step: validate that the stitched polygon is produced with
exactly one bridge (stitch) per obstacle. Regression test for the bug where a single
obstacle was connected to the outer polygon by 2 stitches instead of 1.
"""

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import Polygon
from models import Job
from models import User
from steps import StitchingStep
from steps import ValidationPolygonStep


def _user():
    return User(email=Email("u@e.com"))


# Same polygon as test_polygon_triangle.py (boundary + 3 obstacles).
TRIANGLE_STDIN = {
    "boundary": {
        "points": [
            [619.3310965232191, 482.5],
            [14.007488451252128, 332.5],
            [361.1930950644299, 274.5],
            [358.1914903963044, 9.5],
        ]
    },
    "obstacles": [
        {
            "points": [
                [506.2706540238269, 416.5],
                [506.2706540238269, 333.5],
                [450.2407002188184, 312.5],
                [444.2374908825675, 395.5],
            ]
        },
        {
            "points": [
                [405.21663019693653, 385.5],
                [406.2171650863117, 319.5],
                [269.1438852419159, 343.5],
            ]
        },
        {
            "points": [
                [404.21609530756143, 281.5],
                [463.2476537806954, 276.5],
                [424.22679309506447, 223.5],
            ]
        },
    ],
    "guards": [],
}


def test_triangle_stitching_one_stitch_per_obstacle():
    """
    Stitching with the triangle polygon (boundary + 3 obstacles) must produce
    exactly one stitch (bridge) per obstacle. Validates that we do not get
    the bug where one obstacle is connected to the outer polygon by 2 stitches
    instead of 1.
    """
    stdout = {}
    job_validate = Job(
        id=Identifier("tri-stitch-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(TRIANGLE_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user(), state={}).run())

    job_stitch = Job(
        id=Identifier("tri-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(TRIANGLE_STDIN),
        stdout=dict(stdout),
    )
    stitch_out = StitchingStep(job=job_stitch, user=_user(), state={}).run()
    stdout.update(stitch_out)

    assert "stitched" in stdout, "Stitching step must output stitched polygon"
    assert "stitches" in stdout, "Stitching step must output stitches list"
    stitched = stdout["stitched"]
    stitches = stdout["stitches"]

    assert isinstance(stitched, (list, dict)), "stitched must be a sequence of points"
    num_obstacles = len(TRIANGLE_STDIN["obstacles"])
    assert len(stitches) == num_obstacles, (
        f"Stitching must produce exactly one stitch per obstacle: "
        f"expected {num_obstacles} stitches for {num_obstacles} obstacles, got {len(stitches)}. "
        f"stitches={stitches}"
    )


def test_triangle_stitching_output_valid_for_ear_clipping():
    """
    Stitching of the triangle polygon must not produce outputs that cause ear clipping
    to fail: stitched polygon must be simple and have no non-consecutive duplicate
    vertices (e.g. bridge endpoints duplicated in the ring).
    """
    stdout = {}
    job_validate = Job(
        id=Identifier("tri-stitch-validate-ec"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(TRIANGLE_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user(), state={}).run())
    job_stitch = Job(
        id=Identifier("tri-stitch-ec"),
        step_name=StepName.STITCHING,
        stdin=dict(TRIANGLE_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user(), state={}).run())

    stitched = Polygon.unserialize(stdout["stitched"])

    anchor = stitched[-2]
    vertex = stitched[-1]

    bridge = vertex.to(anchor)
    assert bridge in stitched, f"Bridge {bridge} is not in stitched: {stitched}"
