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
from models import Job
from models import User
from steps import EarClippingStep


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
    True if any edge of the ear crosses or overlaps any edge of the stitched polygon,
    except when the ear edge is the same as a stitched edge.
    Returns (has_violation, message) for assertions.
    """
    stitched_edges = list(stitched.edges)
    for ear_edge in ear.edges:
        for stitched_edge in stitched_edges:
            if _segment_same(ear_edge, stitched_edge):
                continue
            if ear_edge.intersects(stitched_edge, inclusive=False):
                return (
                    True,
                    f"Ear edge {ear_edge[0]}–{ear_edge[1]} crosses stitched edge {stitched_edge[0]}–{stitched_edge[1]} (interior intersection)",
                )
            if ear_edge.contains(stitched_edge.midpoint, inclusive=False) or stitched_edge.contains(
                ear_edge.midpoint, inclusive=False
            ):
                return (
                    True,
                    f"Ear edge {ear_edge[0]}–{ear_edge[1]} overlaps stitched edge {stitched_edge[0]}–{stitched_edge[1]}",
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
