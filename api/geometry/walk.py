"""
Walk type: three Points (start, center, end) with signed_area and orientation.

Title
-----
Walk (Three-Point Turn)

Context
-------
Walk represents three consecutive points (start, center, end) and computes
the signed area (2x2 determinant) and Orientation (COLLINEAR, CLOCKWISE,
COUNTER_CLOCKWISE). Used by Segment.contains (collinearity check), Polygon
is_convex (all turns same orientation), and orientation tests. Indexable as [0]=start, [1]=center, [2]=end. Iterable: for p in walk yields
start, center, end. is_cw(), is_ccw(), is_collinear() are convenience predicates.

Examples:
>>> walk = Walk(start=p0, center=p1, end=p2)
>>> walk.orientation  # Orientation.CLOCKWISE
>>> walk.is_collinear()
"""

from __future__ import annotations

from decimal import Decimal
from functools import cached_property
from typing import Iterator

from attributes import Signature
from enums import Orientation
from geometry.point import Point
from geometry.point import PointLike


class Walk:
    def __init__(self, *, start: PointLike, center: PointLike, end: PointLike) -> None:
        if isinstance(start, Point):
            self.start = start
        else:
            self.start = Point.unserialize(start)
        if isinstance(center, Point):
            self.center = center
        else:
            self.center = Point.unserialize(center)
        if isinstance(end, Point):
            self.end = end
        else:
            self.end = Point.unserialize(end)

    @cached_property
    def signed_area(self) -> Decimal:
        if self[0] == self[1] or self[1] == self[2] or self[0] == self[2]:
            return Decimal("0")
        u = self[1] - self[0]
        v = self[2] - self[0]
        # 2x2 determinant: u.x*v.y - u.y*v.x
        return (u.x * v.y - u.y * v.x) / Decimal("2")

    @property
    def orientation(self) -> Orientation:
        if self.signed_area == Decimal("0"):
            return Orientation.COLLINEAR
        if self.signed_area > Decimal("0"):
            return Orientation.COUNTER_CLOCKWISE
        return Orientation.CLOCKWISE

    def is_cw(self) -> bool:
        return self.orientation == Orientation.CLOCKWISE

    def is_ccw(self) -> bool:
        return self.orientation == Orientation.COUNTER_CLOCKWISE

    def is_collinear(self) -> bool:
        return self.orientation == Orientation.COLLINEAR

    def __repr__(self) -> str:
        return f"Walk(start={self.start!r}, center={self.center!r}, end={self.end!r})"

    def __hash__(self) -> Signature:
        return Signature(f"{self.start!r}:{self.center!r}:{self.end!r}")

    def __getitem__(self, index: int) -> Point:
        if index == 0:
            return self.start
        elif index == 1:
            return self.center
        elif index == 2:
            return self.end
        raise IndexError("Walk index out of range")

    def __len__(self) -> int:
        return 3

    def __invert__(self) -> Walk:
        """Reverse the walk (swap start and end). CCW becomes CW, collinear stays collinear."""
        return Walk(start=self.end, center=self.center, end=self.start)

    def __iter__(self) -> Iterator[Point]:
        """Yield start, center, end so you can iterate: for p in walk."""
        yield self.start
        yield self.center
        yield self.end
