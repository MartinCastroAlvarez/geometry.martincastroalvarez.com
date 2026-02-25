"""
Polygon type: Sequence of Point (closed chain). __and__ shared edge, is_ccw, is_cw, is_convex.
"""

from __future__ import annotations

from decimal import Decimal

from exceptions import ValidationError

from attributes.point import Point
from attributes.sequence import Sequence
from enums.orientation import Orientation

from geometry.path import Path


class Polygon(Sequence[Point]):
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
                raise ValidationError(
                    f"Polygon item at index {i} must be a Point, got {type(item).__name__}"
                )
        super().__init__(value)

    def __and__(self, other: Polygon) -> Polygon:
        """Shared edge as polygon of two points; raises if polygons do not share an edge (like lab convex)."""
        if not isinstance(other, Polygon):
            return NotImplemented
        n: int = len(self)
        m: int = len(other)
        if n < 2 or m < 2:
            raise ValidationError("Polygons do not share an edge")
        self_edges: set[frozenset] = {
            frozenset({self[i], self[(i + 1) % n]}) for i in range(n)
        }
        other_edges: set[frozenset] = {
            frozenset({other[j], other[(j + 1) % m]}) for j in range(m)
        }
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
            (
                self[i].x * self[(i + 1) % n].y - self[i].y * self[(i + 1) % n].x
                for i in range(n)
            ),
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
            path: Path = Path(
                start=self[i - 1],
                center=self[i],
                end=self[(i + 1) % n],
            )
            if path.is_collinear():
                continue
            if orientation is None:
                orientation = path.orientation
            elif path.orientation != orientation:
                return False
        return orientation is not None
