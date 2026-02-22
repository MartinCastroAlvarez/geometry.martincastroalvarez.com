from __future__ import annotations

from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any

from box import Bounded, Box
from element import Element, Element2D
from exceptions import PolygonDegenerateError, PolygonTooFewPointsError
from path import Path
from point import Point, PointSequence
from segment import Segment, SegmentSequence

if TYPE_CHECKING:
    pass


class Polygon(Bounded, Element2D):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and isinstance(args[0], dict):
            kwargs = args[0]
            args = ()
        if kwargs and "points" in kwargs:
            val = kwargs["points"]
            points = val if isinstance(val, PointSequence) else PointSequence(val)
        elif len(args) == 1 and isinstance(args[0], Polygon):
            points = args[0].points
        elif len(args) == 1:
            points = (
                args[0]
                if isinstance(args[0], PointSequence)
                else PointSequence(args[0])
            )
        else:
            raise PolygonTooFewPointsError("Polygon requires points")
        items: list[Point] = points.items
        deduplicated = [items[0]]
        if items:
            for i in range(1, len(items)):
                if items[i] != items[i - 1]:
                    deduplicated.append(items[i])
        self.points = PointSequence(items=deduplicated)
        if len(self.points) < 3:
            raise PolygonTooFewPointsError("Polygon must have at least 3 points")
        if not (abs(self)):
            raise PolygonDegenerateError("Polygon is degenerate: area is zero")

    def __len__(self) -> int:
        return len(self.points)

    def __getitem__(self, index: int) -> Point:
        return self.points[index]

    def __repr__(self) -> str:
        return f"Polygon({self.points.items!r})"

    @property
    def perimeter(self) -> Decimal:
        return sum((edge.size for edge in self.edges), start=Decimal("0"))

    @cached_property
    def signed_area(self) -> Decimal:
        return self.points.signed_area

    @cached_property
    def edges(self) -> SegmentSequence:
        return self.points.edges

    @cached_property
    def box(self) -> Box:
        min_x: Decimal = min(point[0] for point in self.points)
        max_x: Decimal = max(point[0] for point in self.points)
        min_y: Decimal = min(point[1] for point in self.points)
        max_y: Decimal = max(point[1] for point in self.points)
        return Box(
            bottom_left=Point(x=min_x, y=min_y),
            top_left=Point(x=min_x, y=max_y),
            bottom_right=Point(x=max_x, y=min_y),
            top_right=Point(x=max_x, y=max_y),
        )

    def contains(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, (tuple, list)) and len(obj) == 2:
            obj = Point(x=Decimal(str(obj[0])), y=Decimal(str(obj[1])))

        if isinstance(obj, Point):
            if not self.box.contains(obj, inclusive=inclusive):
                return False

            if inclusive:
                for edge in self.edges:
                    if edge.contains(obj, inclusive=True):
                        return True

            inside: bool = False
            for edge in self.edges:
                if edge.box.y[0] == edge.box.y[1]:
                    continue
                if not edge.box.y.contains(obj[1], inclusive=True):
                    continue
                if edge[0][1] > edge[1][1]:
                    edge = ~edge
                path: Path = Path(start=edge[0], center=edge[1], end=obj)
                if path.is_collinear():
                    return inclusive
                if path.is_ccw():
                    inside = not inside

            return inside

        if isinstance(obj, Segment):
            if not self.box.contains(obj, inclusive=inclusive):
                return False

            if not self.contains(obj[0], inclusive=inclusive):
                return False

            if not self.contains(obj[1], inclusive=inclusive):
                return False

            for edge in self.edges:
                if edge.intersects(obj):
                    if any(
                        (
                            obj[0] == edge[0],
                            obj[0] == edge[1],
                            obj[1] == edge[0],
                            obj[1] == edge[1],
                        )
                    ):
                        continue
                    return False

            return True

        raise NotImplementedError(f"Polygon.contains not implemented for {type(obj)}")

    def overlaps(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Box):
            return obj.overlaps(self, inclusive=inclusive)

        if isinstance(obj, Segment):
            if any(edge.intersects(obj) for edge in self.edges):
                return True
            if self.contains(obj, inclusive=inclusive):
                return True
            return False

        if isinstance(obj, Polygon):
            if not self.box.overlaps(obj.box, inclusive=inclusive):
                return False

            for e1 in self.edges:
                for e2 in obj.edges:
                    if e1.intersects(e2, inclusive=inclusive):
                        return True

            if self.contains(obj.points[0], inclusive=inclusive):
                return True
            if obj.contains(self.points[0], inclusive=inclusive):
                return True

            return False

        raise NotImplementedError(f"Polygon.overlaps not implemented for {type(obj)}")
