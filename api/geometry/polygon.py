"""
Polygon type: Sequence of Point (closed chain). __and__ shared edge, is_ccw, is_cw, is_convex, ray.

Title
-----
Polygon (Closed Chain of Points)

Context
-------
Polygon is a closed sequence of Points representing a boundary or obstacle.
It implements Volume (signed_area), Spatial (contains, intersects), Bounded
(box), and Serializable. edges returns consecutive Segment (with wrap).
contains and intersects support Point, Segment, Box, Polygon. ray(point) uses
horizontal ray casting (odd crossings = inside). __and__(other) returns the
shared edge as a two-point polygon; raises if no shared edge. is_ccw, is_cw,
is_convex use Walk orientation. Used for gallery boundary, obstacles, and all
polygon-based geometry in the pipeline.

Examples:
>>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
>>> poly.edges
>>> poly.contains(Point((0.5, 0.5)))
>>> poly.ray(Point((0.5, 0.5)))
>>> shared = poly1 & poly2
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from enums import Orientation
from enums import PolygonSortMode
from exceptions import PolygonBoxRequiresOnePointError
from exceptions import PolygonItemMustBePointError
from exceptions import PolygonsDoNotShareEdgeError
from exceptions import PolygonUnserializeExpectsListError
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

    Context
    -------
    Vertices form a closed loop; constructor checks each vertex has degree 2
    (exactly two incident edges) so the polygon is a single closed chain.

    Example
    -------
    >>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
    >>> len(poly.edges)
    4
    """

    def __init__(
        self,
        value: list[Point] | None = None,
    ) -> None:
        """Build polygon from list of Point; raises if any item is not a Point. Simplicity is not validated here."""
        if value is None:
            value = []
        if not isinstance(value, list):
            value = list(value) if value is not None else []
        for i, item in enumerate(value):
            if not isinstance(item, Point):
                raise PolygonItemMustBePointError(f"Polygon item at index {i} must be a Point, got {type(item).__name__}")
        super().__init__(value)

    @property
    def rightmost(self) -> Point:
        """Rightmost vertex by (x, y) order; used for bridge anchor in stitching."""
        if not self:
            raise PolygonBoxRequiresOnePointError("Polygon.rightmost requires at least one point")
        return max(self, key=lambda p: (p.x, p.y))

    def degree(self, point: Point) -> int:
        """
        Return 2 times the number of times the point appears as a vertex.

        Context
        -------
        Each occurrence of a vertex contributes 2 to the degree (two incident
        edges). Simple polygon requires degree 2 for every vertex.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> poly.degree(Point((0, 0)))
        2
        """
        return 2 * len([v for v in self if (v.x, v.y) == (point.x, point.y)])

    def __contains__(self, obj: object) -> bool:
        """Element in self, or Segment as contiguous subsequence (with wrap), or delegate to Sequence."""
        if isinstance(obj, Segment):
            if len(self) < 2:
                return False
            try:
                i: int = self.index(obj[0])
            except ValueError:
                return False
            if self[i + 1] == obj[1]:
                return True
            if self[i - 1] == obj[1]:
                return True
            return False
        return list.__contains__(self, obj)

    @property
    def edges(self) -> Sequence[Segment]:
        """
        Consecutive edges as Segment (wrap-around from last to first vertex).

        Context
        -------
        Uses Sequence slicing so the edge from the last vertex to the first
        is included. Empty or single-point polygon returns empty sequence.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> len(poly.edges)
        4
        """
        n: int = len(self)
        if n < 2:
            return Sequence([])
        return Sequence([Segment(list(self[i : i + 2])) for i in range(n)])

    @property
    def box(self) -> Box:
        """
        Axis-aligned bounding box of the polygon vertices.

        Context
        -------
        Min/max of x and y over all vertices. Requires at least one point.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [2, 0], [2, 3], [0, 3]])
        >>> poly.box.bottom_left, poly.box.top_right
        (Point(...), Point(...))
        """
        if not self:
            raise PolygonBoxRequiresOnePointError("Polygon.box requires at least one point")
        xs: list[Decimal] = [point.x for point in self]
        ys: list[Decimal] = [point.y for point in self]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return Box(
            bottom_left=Point((min_x, min_y)),
            top_left=Point((min_x, max_y)),
            bottom_right=Point((max_x, min_y)),
            top_right=Point((max_x, max_y)),
        )

    def contains(self, obj: Any, inclusive: bool = True) -> bool:
        """
        Return True if this polygon contains obj (Point, Segment, or Polygon).

        Context
        -------
        Point: fast box test, then ray(point) if not on boundary. Segment:
        endpoints and midpoint inside, no proper edge crossing. Polygon: all
        vertices of other inside. inclusive controls boundary inclusion.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> poly.contains(Point((0.5, 0.5)))
        True
        """
        if isinstance(obj, Point):
            if not self.box.contains(obj, inclusive=inclusive):
                return False
            if inclusive:
                for edge in self.edges:
                    if edge.contains(obj, inclusive=True):
                        return True
            return self.ray(obj)

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
            return all(self.contains(point, inclusive=inclusive) for point in obj)
        raise NotImplementedError(f"Polygon.contains only supports Point, Segment, Polygon; got {type(obj).__name__}")

    def ray(self, point: Point) -> bool:
        """
        Return True if point is inside the polygon (point-in-polygon).

        Context
        -------
        Uses horizontal ray casting to the right; odd number of edge crossings
        means inside, even means outside. Degenerate (y on edge) handled by
        consistent ordering. Only used when point is inside the bounding box
        and not on any edge.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [2, 0], [2, 2], [0, 2]])
        >>> poly.ray(Point((1, 1)))
        True
        >>> poly.ray(Point((3, 1)))
        False
        """
        n: int = len(self)
        if n < 3:
            return False
        crossings: int = 0
        for i in range(n):
            a: Point = self[i]
            b: Point = self[i + 1]
            if a.y > b.y:
                a, b = b, a
            if point.y < a.y or point.y > b.y:
                continue
            if a.y == b.y:
                continue
            t: float = (point.y - a.y) / (b.y - a.y)
            x_intersect: float = a.x + t * (b.x - a.x)
            if x_intersect > point.x:
                crossings += 1
        return crossings % 2 == 1

    def intersects(self, obj: Any, inclusive: bool = True) -> bool:
        """
        Return True if this polygon intersects obj (Point, Segment, Box, or Polygon).

        Context
        -------
        Point: same as contains. Segment: shared boundary or interior overlap.
        Box: any vertex inside box, any box corner inside polygon, or any
        edge-edge intersection. Polygon: vertex containment or edge crossing.
        inclusive controls boundary inclusion.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> poly.intersects(Point((0.5, 0.5)))
        True
        """
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
            for point in self:
                if obj.contains(point, inclusive=inclusive):
                    return True
            for corner in (
                obj.bottom_left,
                obj.top_left,
                obj.bottom_right,
                obj.top_right,
            ):
                if self.contains(corner, inclusive=inclusive):
                    return True
            for edge in self.edges:
                for box_edge in obj.edges:
                    if edge.intersects(box_edge, inclusive=inclusive):
                        return True
            return False

        if isinstance(obj, Polygon):
            if not self.box.intersects(obj.box, inclusive=inclusive):
                return False
            for point in self:
                if obj.contains(point, inclusive=inclusive):
                    return True
            for point in obj:
                if self.contains(point, inclusive=inclusive):
                    return True
            for edge in self.edges:
                for other_edge in obj.edges:
                    if edge.intersects(other_edge, inclusive=inclusive):
                        return True
            return False
        raise NotImplementedError(f"Polygon.intersects only supports Point, Segment, Box, Polygon; got {type(obj).__name__}")

    def serialize(self) -> list[list[Any]]:
        """
        Return list of point coords (each point as list [x, y]).

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [1, 1]])
        >>> poly.serialize()
        [[0, 0], [1, 1]]
        """
        return [json.loads(point.serialize()) for point in self]

    @classmethod
    def unserialize(cls, data: list[Any]) -> Polygon:
        """
        Build Polygon from list of point coords; each point validated via Point.unserialize.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> len(poly)
        4
        """
        if not isinstance(data, list):
            raise PolygonUnserializeExpectsListError("Polygon.unserialize expects a list of points")
        return cls([Point.unserialize(item) for item in data])

    def __and__(self, other: Polygon) -> Polygon:
        """
        Return shared edge as polygon of two points; raises if no shared edge.

        Context
        -------
        Used for adjacent convex components (e.g. in lab). Edges compared as
        frozenset of endpoints; exactly one shared edge required.

        Example
        -------
        >>> p1 = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> p2 = Polygon.unserialize([[1, 0], [2, 0], [2, 1], [1, 1]])
        >>> (p1 & p2)
        Polygon([Point(...), Point(...)])
        """
        if not isinstance(other, Polygon):
            return NotImplemented
        n: int = len(self)
        m: int = len(other)
        if n < 2 or m < 2:
            raise PolygonsDoNotShareEdgeError("Polygons do not share an edge")
        self_edges: set[frozenset[Point]] = {frozenset({self[i], self[(i + 1) % n]}) for i in range(n)}
        other_edges: set[frozenset[Point]] = {frozenset({other[j], other[(j + 1) % m]}) for j in range(m)}
        shared: set[frozenset[Point]] = self_edges & other_edges
        if not shared:
            raise PolygonsDoNotShareEdgeError("Polygons do not share an edge")
        edge_key: frozenset[Point] = shared.pop()
        a: Point
        b: Point
        a, b = edge_key
        return Polygon([a, b])

    @property
    def signed_area(self) -> Decimal:
        """
        Signed area via sum of 2x2 determinants (point i, point i+1); divide by 2.

        Context
        -------
        Shoelace formula; positive for counter-clockwise, negative for clockwise.
        Zero for fewer than 3 vertices.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> poly.signed_area
        Decimal('1')
        """
        n: int = len(self)
        if n < 3:
            return Decimal("0")
        area2: Decimal = sum(
            (self[i].x * self[(i + 1) % n].y - self[i].y * self[(i + 1) % n].x for i in range(n)),
            start=Decimal("0"),
        )
        return area2 / Decimal("2")

    def is_ccw(self) -> bool:
        """Return True if polygon has at least 3 vertices and positive signed area (counter-clockwise)."""
        return len(self) >= 3 and self.signed_area > Decimal("0")

    def is_cw(self) -> bool:
        """Return True if polygon has at least 3 vertices and negative signed area (clockwise)."""
        return len(self) >= 3 and self.signed_area < Decimal("0")

    def sort(
        self,
        sort_mode: str | PolygonSortMode = PolygonSortMode.DEFAULT,
    ) -> Polygon:
        """
        Sort polygon in place. Return self for chaining.

        sort_mode: "default" (or PolygonSortMode.DEFAULT) sorts vertices by (point.x, point.y).
        "ccw" / PolygonSortMode.CCW ensures counter-clockwise orientation (reverses if needed).
        "cw" / PolygonSortMode.CW ensures clockwise orientation (reverses if needed).
        Invalid sort_mode raises InvalidPolygonSortModeError from exceptions.
        """
        mode: PolygonSortMode = PolygonSortMode.parse(sort_mode)
        if mode == PolygonSortMode.DEFAULT:
            list.sort(self, key=lambda p: (p.x, p.y))
        elif mode == PolygonSortMode.CCW:
            if not self.is_ccw():
                self.reverse()
        elif mode == PolygonSortMode.CW:
            if not self.is_cw():
                self.reverse()
        return self

    def is_convex(self) -> bool:
        """
        Return True if every vertex has the same turn orientation (no reflex vertices).

        Context
        -------
        Uses Walk for each vertex (prev, curr, next); first non-collinear turn
        sets orientation, any opposite turn means not convex.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> poly.is_convex()
        True
        """
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
        Return True if the polygon is a simple closed chain: every vertex has degree 2
        and no two non-adjacent edges intersect (proper crossing).

        Context
        -------
        Simple means: (1) at least 3 vertices, (2) each vertex appears with exactly
        two incident edges (closed chain, no branches or self-touch), (3) non-adjacent
        edges do not cross. Adjacent edges share a vertex; non-adjacent may only touch
        at a shared vertex. ValidationPolygonStep.run() validates boundary and obstacles
        are simple and raises PolygonNotSimpleError if not.

        Example
        -------
        >>> poly = Polygon.unserialize([[0, 0], [1, 0], [1, 1], [0, 1]])
        >>> poly.is_simple()
        True
        """
        n: int = len(self)
        if n < 3:
            return False
        if any(self.degree(point) != 2 for point in self):
            return False
        edges: Sequence[Segment] = self.edges
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                if (i - j) % n == 1 or (j - i) % n == 1:
                    continue  # adjacent edges share a vertex
                edge_i: Segment = edges[i]
                edge_j: Segment = edges[j]
                if edge_i.intersects(edge_j, inclusive=True) and not edge_i.connects(edge_j):
                    return False
        return True
