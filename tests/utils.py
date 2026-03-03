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
            if edge.connects(seg):
                continue
            if seg.intersects(edge, inclusive=False):
                # Touching at segment endpoint (segment endpoint on obstacle edge) is allowed.
                if edge.contains(seg[0], inclusive=True) or edge.contains(seg[1], inclusive=True):
                    continue
                return (
                    False,
                    f"segment {seg[0]}–{seg[1]} intersects obstacle {oi} edge {ei} ({edge[0]}–{edge[1]})",
                )
    return (True, "")


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
    After ear clipping: validate that no ear has a segment (vertex–vertex or
    vertex–edge-midpoint) that intersects or crosses any obstacle. Touching
    obstacle edges at endpoints is allowed.
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
        for i in range(n):
            for edge in ear.edges:
                seg = ear[i].to(edge.midpoint)
                ok, msg = _segment_clear_of_obstacles(seg, obstacles)
                if not ok:
                    raise AssertionError(
                        f"Ear {ear_id} has segment from vertex {i} to edge midpoint {edge.midpoint} that crosses obstacle: {msg}. "
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
