"""
Unit tests for ear clipping: given a stitched polygon (sequence of points), run ear clipping
and validate that every produced ear is valid and that no ear edge crosses or overlaps any
edge of the stitched polygon, except when the ear edge is the same as a stitched edge.
"""

from decimal import Decimal

from attributes import Email
from attributes import Identifier
from enums import StepName
from geometry import Ear
from geometry import Point
from geometry import Polygon
from geometry import Segment
from geometry.polygon import _segments_share_endpoint
from geometry import Walk
from models import Job
from models import User
from steps import EarClippingStep
from steps import StitchingStep
from steps import ValidationPolygonStep


def _point(x: int | float | Decimal, y: int | float | Decimal) -> Point:
    return Point([Decimal(x), Decimal(y)])


def _stitched_polygon(points: list[tuple[int | float, int | float]]) -> Polygon:
    """Build a polygon from a list of (x, y) for use as stitched."""
    return Polygon([_point(x, y) for x, y in points])


def _user() -> User:
    return User(email=Email("u@e.com"))


def _run_ear_clipping(stitched: Polygon) -> list[Ear]:
    """Run ear clipping on stitched; return list of ears."""
    stdout = {
        "boundary": stitched.serialize(),
        "stitched": stitched.serialize(),
        "obstacles": [],
    }
    job = Job(
        id=Identifier("ears-test"),
        step_name=StepName.EAR_CLIPPING,
        stdin={},
        stdout=stdout,
    )
    step = EarClippingStep(job=job, user=_user())
    out = step.run()
    ears_ser = out["ears"]
    if isinstance(ears_ser, dict):
        return [Ear.unserialize(ser) for ser in ears_ser.values()]
    return [Ear.unserialize(ser) for ser in ears_ser]


def _segment_same(a: Segment, b: Segment) -> bool:
    """True if both segments have the same two endpoints (order irrelevant)."""
    return a == b


def _ear_edge_crosses_or_overlaps_stitched(ear: Ear, stitched: Polygon) -> tuple[bool, str]:
    """
    True if any edge of the ear crosses (interior intersection) any edge of the stitched polygon,
    except when the ear edge is the same as a stitched edge.
    Collinear edges and segments that only share an endpoint or have a point on the other edge are allowed.
    Returns (has_violation, message) for assertions.
    """
    stitched_edges = list(stitched.edges)
    for ear_edge in ear.edges:
        for stitched_edge in stitched_edges:
            if _segment_same(ear_edge, stitched_edge):
                continue
            if _segments_share_endpoint(ear_edge, stitched_edge):
                continue
            if ear_edge.crosses(stitched_edge):
                return (
                    True,
                    f"Ear edge {ear_edge[0]}–{ear_edge[1]} crosses stitched edge {stitched_edge[0]}–{stitched_edge[1]} (interior intersection)",
                )
    return (False, "")


def test_ears_square_stitched_no_cross_no_overlap():
    """Stitched = square (0,0),(1,0),(1,1),(0,1). All ears must not cross or overlap stitched edges."""
    stitched = _stitched_polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    ears = _run_ear_clipping(stitched)
    assert len(ears) == 2, "Square triangulation must produce 2 ears"
    for ear in ears:
        assert ear.is_convex() and ear.is_simple()
        ok, msg = _ear_edge_crosses_or_overlaps_stitched(ear, stitched)
        assert not ok, msg


def test_ears_pentagon_stitched_no_cross_no_overlap():
    """Stitched = convex pentagon. All ears must not cross or overlap stitched edges."""
    stitched = _stitched_polygon([(0, 0), (2, 0), (2.5, 1.5), (1, 2), (-0.5, 1)])
    ears = _run_ear_clipping(stitched)
    assert len(ears) == 3, "Pentagon triangulation must produce 3 ears"
    for ear in ears:
        assert ear.is_convex() and ear.is_simple()
        ok, msg = _ear_edge_crosses_or_overlaps_stitched(ear, stitched)
        assert not ok, msg


def test_ears_hexagon_stitched_no_cross_no_overlap():
    """Stitched = convex hexagon. All ears must not cross or overlap stitched edges."""
    stitched = _stitched_polygon([(0, 0), (1, 0), (1.5, 0.8), (1, 1.6), (0, 1.6), (-0.5, 0.8)])
    ears = _run_ear_clipping(stitched)
    assert len(ears) == 4, "Hexagon triangulation must produce 4 ears"
    for ear in ears:
        assert ear.is_convex() and ear.is_simple()
        ok, msg = _ear_edge_crosses_or_overlaps_stitched(ear, stitched)
        assert not ok, msg


def test_ears_triangle_stitched_single_ear():
    """Stitched = single triangle. One ear equal to stitched; no crossing."""
    stitched = _stitched_polygon([(0, 0), (2, 0), (1, 1)])
    ears = _run_ear_clipping(stitched)
    assert len(ears) == 1, "Triangle must produce 1 ear"
    ear = ears[0]
    assert ear.is_convex() and ear.is_simple()
    ok, msg = _ear_edge_crosses_or_overlaps_stitched(ear, stitched)
    assert not ok, msg


def test_ears_no_collinear_even_when_input_has_consecutive_equal_points():
    """
    When the input polygon has a sequence of equal points, Polygon (Sequence) dedups them
    automatically. Ear clipping must not produce any collinear ear.
    """
    # Square with (1,0) repeated three times; Sequence.dedup() in Polygon constructor removes contiguous duplicates.
    stitched = Polygon([_point(x, y) for x, y in [(0, 0), (1, 0), (1, 0), (1, 0), (1, 1), (0, 1)]])
    assert len(stitched) == 4, "dedup() must reduce to 4 vertices"
    ears = _run_ear_clipping(stitched)
    assert len(ears) == 2, "Deduped square must produce 2 ears"
    for ear in ears:
        assert not Walk(start=ear[0], center=ear[1], end=ear[2]).is_collinear(), (
            f"Ear must not be collinear; got ear with points {ear[0]}, {ear[1]}, {ear[2]}"
        )
        assert ear.is_convex() and ear.is_simple()


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


def test_triangle_polygon_ear_clipping_output():
    """
    Run validation, stitching, then ear clipping for the triangle polygon.
    Assert ear clipping output: ear count, ears simple and convex, no obstacle intersection.
    """
    from tests.utils import assert_ears_no_obstacle_intersection
    from tests.utils import assert_ears_simple_and_convex

    stdout = {}
    job_validate = Job(
        id=Identifier("tri-ears-validate"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(TRIANGLE_STDIN),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(
        id=Identifier("tri-ears-stitch"),
        step_name=StepName.STITCHING,
        stdin=dict(TRIANGLE_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    job_ear = Job(
        id=Identifier("tri-ears-run"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(TRIANGLE_STDIN),
        stdout=dict(stdout),
    )
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())

    n_stitched = len(Polygon.unserialize(stdout["stitched"]))
    assert len(stdout["ears"]) == n_stitched - 2, (
        f"Expected {n_stitched - 2} ears; got {len(stdout['ears'])}"
    )
    assert_ears_simple_and_convex(stdout["ears"])
    assert_ears_no_obstacle_intersection(stdout["ears"], stdout["obstacles"])


def _run_validate_stitch_ear_clip(stdin: dict, job_prefix: str, tolerance: int = 0):
    """Run validation, stitching, ear clipping; return stdout. Used by example polygon tests."""
    from tests.utils import assert_ears_no_obstacle_intersection
    from tests.utils import assert_ears_simple_and_convex

    stdout = {}
    job_validate = Job(
        id=Identifier(f"{job_prefix}-v"),
        step_name=StepName.VALIDATE_POLYGONS,
        stdin=dict(stdin),
    )
    stdout.update(ValidationPolygonStep(job=job_validate, user=_user()).run())
    job_stitch = Job(
        id=Identifier(f"{job_prefix}-s"),
        step_name=StepName.STITCHING,
        stdin=dict(stdin),
        stdout=dict(stdout),
    )
    stdout.update(StitchingStep(job=job_stitch, user=_user()).run())
    job_ear = Job(
        id=Identifier(f"{job_prefix}-e"),
        step_name=StepName.EAR_CLIPPING,
        stdin=dict(stdin),
        stdout=dict(stdout),
    )
    stdout.update(EarClippingStep(job=job_ear, user=_user()).run())
    n_stitched = len(Polygon.unserialize(stdout["stitched"]))
    assert len(stdout["ears"]) == n_stitched - 2 - tolerance, (
        f"Expected {n_stitched - 2 - tolerance} ears; got {len(stdout['ears'])}"
    )
    assert_ears_simple_and_convex(stdout["ears"])
    assert_ears_no_obstacle_intersection(stdout["ears"], stdout["obstacles"])
