from __future__ import annotations

from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any

from box import Bounded, Box
from element import Element, Element2D
from matrix import Matrix
from path import Path
from point import Point, PointSequence
from segment import Segment, SegmentSequence

if TYPE_CHECKING:
    from polygon import Polygon


class Triangle(Bounded, Element2D):
    def __init__(self, *, left: Any, center: Any, right: Any) -> None:
        self.left = left if isinstance(left, Point) else Point(left)
        self.center = center if isinstance(center, Point) else Point(center)
        self.right = right if isinstance(right, Point) else Point(right)

    def __repr__(self) -> str:
        return f"Triangle({self.left}, {self.center}, {self.right})"

    def __str__(self) -> str:
        return self.__repr__()

    @cached_property
    def signed_area(self) -> Decimal:
        u = self[1] - self[0]
        v = self[2] - self[0]
        matrix = Matrix([u, v])
        return matrix.determinant / Decimal("2")

    @property
    def centroid(self) -> Point:
        return Point(
            x=(self[0].x + self[1].x + self[2].x) / 3,
            y=(self[0].y + self[1].y + self[2].y) / 3,
        )

    @cached_property
    def polygon(self) -> Polygon:
        from polygon import Polygon

        return Polygon(points=PointSequence([self[0], self[1], self[2]]))

    def __getitem__(self, index: int) -> Point:
        if index == 0:
            return self.left
        elif index == 1:
            return self.center
        elif index == 2:
            return self.right
        raise IndexError("Triangle index out of range")

    def contains(self, obj: Element, inclusive: bool = True) -> bool:
        return self.polygon.contains(obj, inclusive=inclusive)

    def overlaps(self, obj: Element, inclusive: bool = True) -> bool:
        return self.polygon.overlaps(obj, inclusive=inclusive)

    @cached_property
    def box(self) -> Box:
        min_x: Decimal = min(self[0][0], self[1][0], self[2][0])
        max_x: Decimal = max(self[0][0], self[1][0], self[2][0])
        min_y: Decimal = min(self[0][1], self[1][1], self[2][1])
        max_y: Decimal = max(self[0][1], self[1][1], self[2][1])
        return Box(
            bottom_left=Point(x=min_x, y=min_y),
            top_left=Point(x=min_x, y=max_y),
            bottom_right=Point(x=max_x, y=min_y),
            top_right=Point(x=max_x, y=max_y),
        )

    @cached_property
    def points(self) -> PointSequence:
        return PointSequence([self[0], self[1], self[2]])

    @cached_property
    def edges(self) -> SegmentSequence:
        return SegmentSequence(
            items=[
                Segment(start=self[0], end=self[1]),
                Segment(start=self[1], end=self[2]),
                Segment(start=self[2], end=self[0]),
            ]
        )

    @property
    def path(self) -> Path:
        return Path(start=self[0], center=self[1], end=self[2])

    @property
    def diagonal(self) -> Segment:
        return self.edges[2]
