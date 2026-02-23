from __future__ import annotations

from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any

from box import Bounded, Box
from element import Element, Element2D
from exceptions import PolygonDegenerateError, PolygonTooFewPointsError
from model import Hash
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
        self.points = PointSequence(items=items)
        if len(self.points) < 3:
            raise PolygonTooFewPointsError(
                f"Polygon must have at least 3 points: {self.points}"
            )
        if not (abs(self)):
            raise PolygonDegenerateError(
                f"Polygon is degenerate: area is zero: {self.points}"
            )

    def __hash__(self) -> Hash:
        return self.points.__hash__()

    def __len__(self) -> int:
        return len(self.points)

    def __getitem__(self, index: int) -> Point:
        return self.points[index]

    @cached_property
    def centroid(self) -> Point:
        return self.points.centroid

    def __repr__(self) -> str:
        return f"Polygon({self.points.items!r})"

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

        if isinstance(obj, Point):
            if not self.box.contains(obj, inclusive=inclusive):
                return False

            if any(edge.contains(obj, inclusive=True) for edge in self.edges):
                return inclusive

            inside: bool = False
            for edge in self.edges:
                if edge.box.y[0] == edge.box.y[1]:
                    continue

                if edge[0][1] > edge[1][1]:
                    edge = ~edge

                if not (edge[0][1] <= obj[1] < edge[1][1]):
                    continue

                if (
                    edge[0][0]
                    + (obj[1] - edge[0][1])
                    * (edge[1][0] - edge[0][0])
                    / (edge[1][1] - edge[0][1])
                    > obj[0]
                ):
                    inside = not inside

            return inside

        if isinstance(obj, Segment):
            if not self.box.contains(obj, inclusive=inclusive):
                return False
            if inclusive and obj in self.edges:
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

        raise NotImplementedError(f"Polygon.contains not implemented for {type(obj)}")

    def intersects(self, obj: Element, inclusive: bool = True) -> bool:

        if isinstance(obj, Polygon):
            if not self.box.intersects(obj.box, inclusive=inclusive):
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

        if self.contains(obj, inclusive=inclusive):
            return True

        if isinstance(obj, Box):
            return self.box.intersects(obj, inclusive=inclusive)

        if isinstance(obj, Segment):
            if inclusive and any(
                (
                    any(
                        (
                            edge.contains(obj[0], inclusive=True),
                            edge.contains(obj[1], inclusive=True),
                        )
                    )
                    for edge in self.edges
                )
            ):
                return True
            if any(
                edge.intersects(obj, inclusive=inclusive)
                for edge in self.edges
                if not edge.connects(obj)
            ):
                return True
            return any(
                (
                    self.contains(obj[0], inclusive=inclusive),
                    self.contains(obj[1], inclusive=inclusive),
                    self.contains(obj.midpoint, inclusive=inclusive),
                )
            )

        raise NotImplementedError(f"Polygon.intersects not implemented for {type(obj)}")
