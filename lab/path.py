from __future__ import annotations

from decimal import Decimal
from enum import Enum
from functools import cached_property
from typing import Any

from matrix import Matrix
from point import Point


class Orientation(int, Enum):
    COLLINEAR = 0
    CLOCKWISE = -1
    COUNTER_CLOCKWISE = 1


class Path:
    def __init__(self, *, start: Any, center: Any, end: Any) -> None:
        self.start = start if isinstance(start, Point) else Point(start)
        self.center = center if isinstance(center, Point) else Point(center)
        self.end = end if isinstance(end, Point) else Point(end)

    @cached_property
    def signed_area(self) -> Decimal:
        u = self[1] - self[0]
        v = self[2] - self[0]
        return Matrix([u, v]).determinant / Decimal("2")

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

    def __getitem__(self, index: int) -> Point:
        if index == 0:
            return self.start
        elif index == 1:
            return self.center
        elif index == 2:
            return self.end
        raise IndexError("Path index out of range")
