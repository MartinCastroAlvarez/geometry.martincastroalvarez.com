"""
Shared assertion helpers for polygon pipeline tests.
Validates ears (simple, convex) and convex components (simple, convex, obstacle-safe, visibility).
Raises AssertionError with detailed troubleshooting info on failure.
"""

from __future__ import annotations

from geometry import ConvexComponent
from geometry import Ear
from geometry import Point
from geometry import Polygon
from geometry import Segment
from geometry.polygon import _segments_share_endpoint


def _segment_clear_of_obstacles(seg: Segment, obstacles: list[Polygon]) -> tuple[bool, str]:
    """
    True if segment does not cross any obstacle (interior or obstacle edge in interior).
    Touching obstacle edges at endpoints is allowed.
    Returns (ok, error_message) for troubleshooting.
    """
    for oi, obstacle in enumerate(obstacles):
        if obstacle.contains(seg.midpoint, inclusive=False):
            return (
                False,
                f"segment midpoint {seg.midpoint} is inside obstacle {oi} (vertices: {obstacle.serialize()})",
            )
        for ei, edge in enumerate(obstacle.edges):
            if _segments_share_endpoint(edge, seg):
                continue
            if seg.crosses(edge):
                return (
                    False,
                    f"segment {seg[0]}–{seg[1]} intersects obstacle {oi} edge {ei} ({edge[0]}–{edge[1]})",
                )
    return (True, "")


def assert_no_stitches_share_a_point(stitches_serialized: list) -> None:
    """
    After stitching: validate that no two stitches (bridge segments) share a point.
    stitches_serialized is the list from stdout["stitches"] (list of serialized Segment).
    Raises AssertionError with segment indices and shared point on failure.
    """
    segments = [Segment.unserialize(s) for s in stitches_serialized]
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            pts_i = {segments[i][0], segments[i][1]}
            pts_j = {segments[j][0], segments[j][1]}
            shared = pts_i & pts_j
            if shared:
                raise AssertionError(
                    f"Stitches {i} and {j} share point(s) {shared}. "
                    f"Stitch {i}: {segments[i][0]}–{segments[i][1]}; "
                    f"stitch {j}: {segments[j][0]}–{segments[j][1]}."
                )


def assert_ears_simple_and_convex(ears_serialized: dict) -> None:
    """
    After ear clipping: validate every ear is simple and convex.
    Raises AssertionError with ear_id and serialized data for troubleshooting.
    """
    for ear_id, ear_ser in ears_serialized.items():
        ear = Ear.unserialize(ear_ser)
        if not ear.is_simple():
            raise AssertionError(
                f"Ear {ear_id} is not simple. ear_id={ear_id!r}, serialized={ear_ser}"
            )
        if not ear.is_convex():
            raise AssertionError(
                f"Ear {ear_id} is not convex. ear_id={ear_id!r}, serialized={ear_ser}"
            )


def assert_ears_no_obstacle_intersection(
    ears_serialized: dict,
    obstacles_serialized: list,
) -> None:
    """
    After ear clipping: validate that no ear has a vertex–vertex segment (ear edge
    or diagonal) that crosses any obstacle. Touching obstacle edges at endpoints
    is allowed. Only vertex–vertex segments are checked; the pipeline guarantees
    the diagonal is obstacle-free, and ear edges are polygon edges.
    Raises AssertionError with ear_id and segment/obstacle details for troubleshooting.
    """
    if not obstacles_serialized:
        return
    obstacles = [Polygon.unserialize(obs) for obs in obstacles_serialized]
    for ear_id, ear_ser in ears_serialized.items():
        ear = Ear.unserialize(ear_ser)
        n = len(ear)
        for i in range(n):
            for j in range(i + 1, n):
                seg = ear[i].to(ear[j])
                ok, msg = _segment_clear_of_obstacles(seg, obstacles)
                if not ok:
                    raise AssertionError(
                        f"Ear {ear_id} has segment between vertices {i} and {j} that crosses obstacle: {msg}. "
                        f"ear_id={ear_id!r}, serialized={ear_ser}"
                    )


def assert_convex_components_simple_convex_no_obstacle_intersection(
    components_serialized: dict,
    obstacles_serialized: list,
) -> None:
    """
    After convex component step: validate each component is simple, convex, and
    intersects zero obstacles except by touching obstacle edges (no segment
    vertex–vertex or vertex–edge-midpoint crosses an obstacle).
    Raises AssertionError with component_id and details for troubleshooting.
    """
    obstacles = [Polygon.unserialize(obs) for obs in obstacles_serialized]
    for comp_id, comp_ser in components_serialized.items():
        component = ConvexComponent.unserialize(comp_ser)
        if not component.is_simple():
            raise AssertionError(
                f"Convex component {comp_id} is not simple. comp_id={comp_id!r}, serialized={comp_ser}"
            )
        if not component.is_convex():
            raise AssertionError(
                f"Convex component {comp_id} is not convex. comp_id={comp_id!r}, serialized={comp_ser}"
            )
        n = len(component)
        # Vertex–vertex segments
        for i in range(n):
            for j in range(i + 1, n):
                seg = component[i].to(component[j])
                ok, msg = _segment_clear_of_obstacles(seg, obstacles)
                if not ok:
                    raise AssertionError(
                        f"Convex component {comp_id} has segment between vertices {i} and {j} that crosses obstacle: {msg}. "
                        f"comp_id={comp_id!r}, serialized={comp_ser}"
                    )
        # Vertex–edge-midpoint segments
        for i in range(n):
            for edge in component.edges:
                seg = component[i].to(edge.midpoint)
                ok, msg = _segment_clear_of_obstacles(seg, obstacles)
                if not ok:
                    raise AssertionError(
                        f"Convex component {comp_id} has segment from vertex {i} to edge midpoint {edge.midpoint} that crosses obstacle: {msg}. "
                        f"comp_id={comp_id!r}, serialized={comp_ser}"
                    )


def assert_convex_components_visibility_within_component(
    components_serialized: dict,
    obstacles_serialized: list,
) -> None:
    """
    After convex component step: for each component, from each vertex, every other
    point (vertex or edge midpoint) of that component must be visible (segment
    does not cross any obstacle). Raises AssertionError with component_id, vertex,
    target point, and obstacle/edge info for troubleshooting.
    """
    obstacles = [Polygon.unserialize(obs) for obs in obstacles_serialized]
    for comp_id, comp_ser in components_serialized.items():
        component = ConvexComponent.unserialize(comp_ser)
        points_and_midpoints: list[Point] = list(component) + [
            e.midpoint for e in component.edges
        ]
        for vi, vertex in enumerate(component):
            for target in points_and_midpoints:
                if vertex == target:
                    continue
                seg = vertex.to(target)
                ok, msg = _segment_clear_of_obstacles(seg, obstacles)
                if not ok:
                    raise AssertionError(
                        f"Convex component {comp_id}: vertex {vi} ({vertex}) cannot see point {target} (segment crosses obstacle): {msg}. "
                        f"comp_id={comp_id!r}, serialized={comp_ser}"
                    )


def assert_visibility_segments_inside_boundary(
    guard_out: dict,
    boundary_serialized: list,
    obstacles_serialized: list,
) -> None:
    """
    After guard placement: assert every visibility segment (guard → visible point) lies
    inside the boundary and does not cross obstacles. Also asserts the midpoint of each
    segment is inside the boundary (and not inside any obstacle).

    guard_out must have "guards" (dict guard_id -> serialized point) and "visibility"
    (dict guard_id -> list of serialized points). boundary_serialized and
    obstacles_serialized are in Polygon.unserialize format.

    Raises AssertionError with segment/guard/point details on failure.
    """
    boundary = Polygon.unserialize(boundary_serialized)
    obstacles = [Polygon.unserialize(obs) for obs in obstacles_serialized]
    guards_ser = guard_out["guards"]
    visibility_ser = guard_out["visibility"]

    for guard_id, guard_pt_ser in guards_ser.items():
        guard_pt = Point.unserialize(guard_pt_ser)
        visible_list = visibility_ser.get(guard_id, [])
        for point_ser in visible_list:
            visible_pt = Point.unserialize(point_ser)
            segment = guard_pt.to(visible_pt)

            if not boundary.contains(segment, inclusive=True):
                raise AssertionError(
                    f"Visibility segment from guard {guard_pt} to {visible_pt} goes outside boundary. "
                    f"Segment: {segment[0]}–{segment[1]}; boundary contains segment: {boundary.contains(segment, inclusive=True)}."
                )
            if not boundary.contains(segment.midpoint, inclusive=True):
                raise AssertionError(
                    f"Visibility segment midpoint {segment.midpoint} (guard {guard_pt} → {visible_pt}) is outside boundary."
                )
            ok, msg = _segment_clear_of_obstacles(segment, obstacles)
            if not ok:
                raise AssertionError(
                    f"Visibility segment from guard {guard_pt} to {visible_pt} crosses obstacle: {msg}."
                )


def assert_no_redundant_guards(guard_out: dict) -> None:
    """
    After guard placement: assert no guard only sees points already covered by other guards.
    guard_out must have "guards" and "visibility" (dict key -> list of serialized points per guard).
    Raises AssertionError if any guard's visibility is a subset of the combined visibility of the rest.
    """
    guards_ser = guard_out["guards"]
    visibility_ser = guard_out["visibility"]
    if len(guards_ser) <= 1:
        return
    for guard_id in guards_ser:
        visible = visibility_ser.get(guard_id)
        if visible is None:
            continue
        guard_points = set(tuple(p) for p in visible)
        other_points: set = set()
        for oid in guards_ser:
            if oid != guard_id:
                for p in visibility_ser.get(oid, []):
                    other_points.add(tuple(p))
        if guard_points and guard_points.issubset(other_points):
            raise AssertionError(
                f"Guard {guard_id} only sees points already covered by other guards (redundant guard)."
            )


def _coord_to_int(c: str | int | float) -> int:
    """Convert a coordinate string or number to int for display."""
    return int(float(c))


def print_guard_coverage_report(guard_out: dict, title: str) -> None:
    """
    Print a report: each guard and the unique points only this guard covers (not covered by others).
    guard_out must have "guards" and "visibility". Point coordinates are displayed as integers.
    """
    import sys
    guards_ser = guard_out["guards"]
    visibility_ser = guard_out["visibility"]
    lines = [f"\n--- {title} ---"]
    for guard_id, guard_ser in guards_ser.items():
        my_points = set(tuple(p) for p in visibility_ser.get(guard_id, []))
        other_points: set = set()
        for oid in guards_ser:
            if oid != guard_id:
                for p in visibility_ser.get(oid, []):
                    other_points.add(tuple(p))
        unique = my_points - other_points
        guard_display = [_coord_to_int(c) for c in guard_ser] if isinstance(guard_ser, (list, tuple)) else guard_ser
        lines.append(f"Guard {guard_id} at {guard_display}: sees {len(my_points)} points, {len(unique)} unique (not covered by others)")
        unique_sorted = sorted(unique, key=lambda x: (float(x[0]), float(x[1])))
        pts_str = ", ".join(str([_coord_to_int(c) for c in pt]) for pt in unique_sorted)
        lines.append(f"  unique points: {pts_str}")
    lines.append("--- end report ---\n")
    out = "\n".join(lines)
    print(out, flush=True)
    sys.stdout.flush()
