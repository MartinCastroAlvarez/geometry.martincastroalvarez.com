"""
Polygon type: Sequence of Point (closed chain). __and__ shared edge, is_ccw, is_cw, is_convex.

Title
-----
Polygon (Closed Chain of Points)

Context
-------
Polygon is a closed sequence of Points representing a boundary or obstacle.
It implements Volume (signed_area), Spatial (contains, intersects), Bounded
(box), and Serializable. edges returns consecutive Segment (with wrap).
contains and intersects support Point, Segment, Box, Polygon. Ray casting
(point-in-polygon) and edge intersection are used. __and__(other) returns
the shared edge as a two-point polygon; raises if no shared edge. is_ccw,
is_cw, is_convex use Walk orientation. Used for gallery boundary, obstacles,
and all polygon-based geometry in the pipeline.

Examples:
>>> poly = Polygon.unserialize([[0,0], [1,0], [1,1], [0,1]])
>>> poly.edges
>>> poly.contains(point)
>>> shared = poly1 & poly2
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from enums import Orientation
from exceptions import ValidationError
from geometry.box import Box
from geometry.point import Point
from geometry.segment import Segment
from geometry.walk import Walk
from interfaces import Bounded
from interfaces import Serializable
from interfaces import Spatial
from interfaces import Volume
from structs import Sequence


class Polygon(Sequence[Point], Volume, Spatial, Bounded, Serializable[list[Any]]):
    """
    A polygon as a Sequence of Point (closed chain). Items must be Point.
    """

    def __init__(
        self,
        value: list[Point] | None = None,
    ) -> None:
        if value is None:
            value = []
        if not isinstance(value, list):
            value = list(value) if value is not None else []
        for i, item in enumerate(value):
            if not isinstance(item, Point):
                raise ValidationError(f"Polygon item at index {i} must be a Point, got {type(item).__name__}")
        super().__init__(value)

    @property
    def edges(self) -> Sequence[Segment]:
        """Consecutive edges as Segment (uses Sequence slicing for wrap-around)."""
        n: int = len(self)
        if n < 2:
            return Sequence([])
        return Sequence([Segment(list(self[i : i + 2])) for i in range(n)])

    @property
    def box(self) -> Box:
        """Axis-aligned bounding box of the polygon vertices."""
        if not self:
            raise ValidationError("Polygon.box requires at least one point")
        xs = [p.x for p in self]
        ys = [p.y for p in self]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return Box(
            bottom_left=Point((min_x, min_y)),
            top_left=Point((min_x, max_y)),
            bottom_right=Point((max_x, min_y)),
            top_right=Point((max_x, max_y)),
        )

    def contains(self, obj: Any, inclusive: bool = True) -> bool:
        """Return True if this polygon contains obj (Point, Segment, or Polygon)."""
        if isinstance(obj, Point):
            if not self.box.contains(obj, inclusive=inclusive):
                return False
            if inclusive:
                for edge in self.edges:
                    if edge.contains(obj, inclusive=True):
                        return True
            return self._point_in_polygon_ray(obj)

        if isinstance(obj, Segment):
            if not self.box.contains(obj, inclusive=inclusive):
                return False
            if inclusive and any(obj == edge for edge in self.edges):
                return True
            if not self.contains(obj[0], inclusive=inclusive):
                return False
            if not self.contains(obj[1], inclusive=inclusive):
                return False
            if not self.contains(obj.midpoint, inclusive=inclusive):
                return False
            for edge in self.edges:
                if edge.connects(obj):
                    continue
                if edge.intersects(obj, inclusive=True):
                    return False
            return True

        if isinstance(obj, Polygon):
            return all(self.contains(Point((p.x, p.y)), inclusive=inclusive) for p in obj)
        raise NotImplementedError(f"Polygon.contains only supports Point, Segment, Polygon; got {type(obj).__name__}")

    def _point_in_polygon_ray(self, point: Point) -> bool:
        """Ray casting: horizontal ray to the right; odd crossings = inside."""
        n: int = len(self)
        if n < 3:
            return False
        crossings = 0
        for i in range(n):
            a, b = self[i], self[i + 1]
            if a.y > b.y:
                a, b = b, a
            if point.y < a.y or point.y > b.y:
                continue
            if a.y == b.y:
                continue
            t = (point.y - a.y) / (b.y - a.y)
            x_intersect = a.x + t * (b.x - a.x)
            if x_intersect > point.x:
                crossings += 1
        return crossings % 2 == 1

    def intersects(self, obj: Any, inclusive: bool = True) -> bool:
        """Return True if this polygon intersects obj (Point, Segment, Box, or Polygon)."""
        if isinstance(obj, Point):
            return self.contains(obj, inclusive=inclusive)
        if isinstance(obj, Segment):
            if inclusive and any(edge.contains(obj[0], inclusive=True) or edge.contains(obj[1], inclusive=True) for edge in self.edges):
                return True
            for edge in self.edges:
                if edge.connects(obj):
                    continue
                if edge.intersects(obj, inclusive=inclusive):
                    return True
            return (
                self.contains(obj[0], inclusive=inclusive)
                or self.contains(obj[1], inclusive=inclusive)
                or self.contains(obj.midpoint, inclusive=inclusive)
            )
        if isinstance(obj, Box):
            if not self.box.intersects(obj, inclusive=inclusive):
                return False
            for p in self:
                if obj.contains(p, inclusive=inclusive):
                    return True
            box_edges = [
                Segment([obj.bottom_left, obj.bottom_right]),
                Segment([obj.bottom_right, obj.top_right]),
                Segment([obj.top_right, obj.top_left]),
                Segment([obj.top_left, obj.bottom_left]),
            ]
            for corner in (
                obj.bottom_left,
                obj.top_left,
                obj.bottom_right,
                obj.top_right,
            ):
                if self.contains(corner, inclusive=inclusive):
                    return True
            for edge in self.edges:
                for box_edge in box_edges:
                    if edge.intersects(box_edge, inclusive=inclusive):
                        return True
            return False
        if isinstance(obj, Polygon):
            if not self.box.intersects(obj.box, inclusive=inclusive):
                return False
            for p in self:
                if obj.contains(p, inclusive=inclusive):
                    return True
            for p in obj:
                if self.contains(p, inclusive=inclusive):
                    return True
            for e1 in self.edges:
                for e2 in obj.edges:
                    if e1.intersects(e2, inclusive=inclusive):
                        return True
            return False
        raise NotImplementedError(f"Polygon.intersects only supports Point, Segment, Box, Polygon; got {type(obj).__name__}")

    def serialize(self) -> list[list[Any]]:
        """Return list of point coords (each point as list [x, y])."""
        return [json.loads(p.serialize()) for p in self]

    @classmethod
    def unserialize(cls, data: list[Any]) -> Polygon:
        """Build Polygon from list of point coords; each point validated via Point.unserialize."""
        if not isinstance(data, list):
            raise ValidationError("Polygon.unserialize expects a list of points")
        return cls([Point.unserialize(p) for p in data])

    def __and__(self, other: Polygon) -> Polygon:
        """Shared edge as polygon of two points; raises if polygons do not share an edge (like lab convex)."""
        if not isinstance(other, Polygon):
            return NotImplemented
        n: int = len(self)
        m: int = len(other)
        if n < 2 or m < 2:
            raise ValidationError("Polygons do not share an edge")
        self_edges: set[frozenset] = {frozenset({self[i], self[(i + 1) % n]}) for i in range(n)}
        other_edges: set[frozenset] = {frozenset({other[j], other[(j + 1) % m]}) for j in range(m)}
        shared: set[frozenset] = self_edges & other_edges
        if not shared:
            raise ValidationError("Polygons do not share an edge")
        edge_key: frozenset = shared.pop()
        a, b = edge_key
        return Polygon([a, b])

    @property
    def signed_area(self) -> Decimal:
        """Signed area via sum of 2x2 determinants (point i, point i+1); divide by 2 for area."""
        n: int = len(self)
        if n < 3:
            return Decimal("0")
        area2: Decimal = sum(
            (self[i].x * self[(i + 1) % n].y - self[i].y * self[(i + 1) % n].x for i in range(n)),
            start=Decimal("0"),
        )
        return area2 / Decimal("2")

    def is_ccw(self) -> bool:
        return len(self) >= 3 and self.signed_area > Decimal("0")

    def is_cw(self) -> bool:
        return len(self) >= 3 and self.signed_area < Decimal("0")

    def is_convex(self) -> bool:
        n: int = len(self)
        if n < 3:
            return False
        orientation: Orientation | None = None
        for i in range(n):
            walk: Walk = Walk(
                start=self[i - 1],
                center=self[i],
                end=self[(i + 1) % n],
            )
            if walk.is_collinear():
                continue
            if orientation is None:
                orientation = walk.orientation
            elif walk.orientation != orientation:
                return False
        return orientation is not None

    def is_simple(self) -> bool:
        """
        Return True if the polygon is simple (no two non-adjacent edges intersect).
        Non-adjacent edges may only touch at a shared vertex; any proper crossing means not simple.
        """
        n: int = len(self)
        if n < 3:
            return False
        edges: Sequence[Segment] = self.edges
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if (i - j) % n == 1 or (j - i) % n == 1:
                    continue  # adjacent edges share a vertex
                e_i = edges[i]
                e_j = edges[j]
                if e_i.intersects(e_j, inclusive=True) and not e_i.connects(e_j):
                    return False
        return True
