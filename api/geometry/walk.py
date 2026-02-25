"""
Walk type: three Points (start, center, end) with signed_area and orientation (collinear / clockwise / counter-clockwise).
"""

from __future__ import annotations

from decimal import Decimal
from functools import cached_property
from typing import Any

from enums.orientation import Orientation
from geometry.point import Point


class Walk:
    def __init__(self, *, start: Any, center: Any, end: Any) -> None:
        self.start = start if isinstance(start, Point) else Point(start)
        self.center = center if isinstance(center, Point) else Point(center)
        self.end = end if isinstance(end, Point) else Point(end)

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

    def __getitem__(self, index: int) -> Point:
        if index == 0:
            return self.start
        elif index == 1:
            return self.center
        elif index == 2:
            return self.end
        raise IndexError("Walk index out of range")
