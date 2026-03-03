"""
Unit tests for ConvexComponent merge (+) and visibility within merged components.
Builds pairs of ConvexComponents that share an edge, merges them, and asserts the result
is convex and simple and that from every vertex all other points (vertices and edge
midpoints) are visible (segment contained in the polygon). Isolates whether the merge
operation itself preserves the visibility invariant.
"""

from decimal import Decimal

from geometry import ConvexComponent
from geometry import Point
from geometry import Polygon


def _point(x: int | float | Decimal, y: int | float | Decimal) -> Point:
    return Point([Decimal(x), Decimal(y)])


def _merged_visibility_holds(merged: ConvexComponent) -> bool:
    """
    True if from every vertex of merged, every other point (vertex or edge midpoint)
    is visible: the segment vertex->point has its midpoint inside or on merged (inclusive).
    For a convex polygon, any segment between two points on or inside the polygon
    lies inside, so checking the midpoint is sufficient.
    """
    points_and_midpoints: list[Point] = list(merged) + [e.midpoint for e in merged.edges]
    for vi, vertex in enumerate(merged):
        for target in points_and_midpoints:
            if vertex == target:
                continue
            seg = vertex.to(target)
            if not merged.contains(seg.midpoint, inclusive=True):
                return False
    return True


def test_merge_two_triangles_shared_edge_result_convex_simple():
    """Two triangles sharing an edge merge into a convex quadrilateral."""
    # Left: (0,0)-(1,0)-(0,1) CCW. Right: (1,0)-(0,1)-(1,1) CCW. Shared edge (1,0)-(0,1). Merged = square.
    a = _point(0, 0)
    b = _point(1, 0)
    c = _point(0, 1)
    d = _point(1, 1)
    left = ConvexComponent([a, b, c])
    right = ConvexComponent([b, c, d])
    merged = left + right
    assert merged.is_convex(), "Merged component must be convex"
    assert merged.is_simple(), "Merged component must be simple"
    assert len(merged) == 4, "Merge of two triangles over shared edge must have 4 vertices"


def test_merge_two_triangles_every_vertex_sees_all_points():
    """After merging two triangles, from every vertex all other points are visible (segment in polygon)."""
    a = _point(0, 0)
    b = _point(1, 0)
    c = _point(0, 1)
    d = _point(1, 1)
    left = ConvexComponent([a, b, c])
    right = ConvexComponent([b, c, d])
    merged = left + right
    assert _merged_visibility_holds(merged), (
        "From every vertex of the merged component, every other point (vertex or edge midpoint) "
        "must be visible (segment contained in polygon)"
    )


def test_merge_three_triangles_chain_result_convex_simple():
    """Merge three triangles in a chain: (A+B)+C. Result convex and simple with visibility."""
    p0 = _point(0, 0)
    p1 = _point(1, 0)
    p2 = _point(0, 1)
    p3 = _point(1, 1)
    p4 = _point(1.5, 0.5)
    left = ConvexComponent([p0, p1, p2])
    right = ConvexComponent([p1, p2, p3])
    quad = left + right
    tri = ConvexComponent([p1, p3, p4])
    merged = quad + tri
    assert merged.is_convex(), "Chained merge (quad+triangle) must be convex"
    assert merged.is_simple(), "Chained merge must be simple"
    assert _merged_visibility_holds(merged), (
        "After chained merge, every vertex must see all other points"
    )


def test_merge_quad_and_triangle_shared_edge_visibility():
    """Merge a quadrilateral and a triangle along a shared edge; visibility holds."""
    # Quad = (0,0),(1,0),(1,1),(0,1). Triangle on right edge (1,0)-(1,1) with vertex (1.5, 0.5).
    a = _point(0, 0)
    b = _point(1, 0)
    c = _point(1, 1)
    d = _point(0, 1)
    e = _point(1.5, 0.5)
    left = ConvexComponent([a, b, d])
    right = ConvexComponent([b, d, c])
    quad = left + right
    tri = ConvexComponent([b, c, e])
    merged = quad + tri
    assert merged.is_convex() and merged.is_simple()
    assert _merged_visibility_holds(merged), (
        "Merged quad+triangle: every vertex must see all other points"
    )


def test_merge_non_adjacent_raises():
    """Merging two components that do not share an edge must raise."""
    from exceptions import PolygonsDoNotShareEdgeError

    # Two disjoint triangles.
    left = ConvexComponent([_point(0, 0), _point(1, 0), _point(0.5, 1)])
    right = ConvexComponent([_point(3, 0), _point(4, 0), _point(3.5, 1)])
    try:
        _ = left + right
        assert False, "Expected PolygonsDoNotShareEdgeError when merging non-adjacent components"
    except PolygonsDoNotShareEdgeError:
        pass
