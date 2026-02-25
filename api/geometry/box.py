"""
Box type: axis-aligned box defined by four corner Points; implements Spatial and Serializable.
"""

from __future__ import annotations

from typing import Any

from exceptions import BoxInvalidEdgeError
from exceptions import SerializedInvalidDictError

from attributes.interval import Interval
from attributes.point import Point
from interfaces.serializable import Serializable
from interfaces.spatial import Spatial


class Box(Spatial, Serializable):
    def to_dict(self) -> dict[str, Any]:
        return {
            "bottom_left": self.bottom_left.to_list(),
            "top_left": self.top_left.to_list(),
            "bottom_right": self.bottom_right.to_list(),
            "top_right": self.top_right.to_list(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Box:
        if not isinstance(data, dict):
            raise SerializedInvalidDictError(
                f"Box.from_dict expects a dict, got {type(data).__name__}"
            )
        for key in ("bottom_left", "top_left", "bottom_right", "top_right"):
            if key not in data:
                raise BoxInvalidEdgeError(f"Box.from_dict missing key {key!r}")
        return cls(
            bottom_left=Point.from_list(data["bottom_left"]),
            top_left=Point.from_list(data["top_left"]),
            bottom_right=Point.from_list(data["bottom_right"]),
            top_right=Point.from_list(data["top_right"]),
        )

    def __init__(
        self,
        *,
        bottom_left: Any,
        top_left: Any,
        bottom_right: Any,
        top_right: Any,
    ) -> None:
        self.bottom_left = (
            bottom_left if isinstance(bottom_left, Point) else Point(bottom_left)
        )
        self.top_left = top_left if isinstance(top_left, Point) else Point(top_left)
        self.bottom_right = (
            bottom_right if isinstance(bottom_right, Point) else Point(bottom_right)
        )
        self.top_right = top_right if isinstance(top_right, Point) else Point(top_right)
        self._validate()

    def _validate(self) -> None:
        if self.bottom_left.x != self.top_left.x:
            raise BoxInvalidEdgeError(
                f"Box must have vertical left edge: {self.bottom_left.x} != {self.top_left.x}"
            )
        if self.bottom_right.x != self.top_right.x:
            raise BoxInvalidEdgeError(
                f"Box must have vertical right edge: {self.bottom_right.x} != {self.top_right.x}"
            )
        if self.bottom_left.y != self.bottom_right.y:
            raise BoxInvalidEdgeError(
                f"Box must have horizontal bottom edge: {self.bottom_left.y} != {self.bottom_right.y}"
            )
        if self.top_left.y != self.top_right.y:
            raise BoxInvalidEdgeError(
                f"Box must have horizontal top edge: {self.top_left.y} != {self.top_right.y}"
            )

    @property
    def x(self) -> Interval:
        return Interval([
            min(self[0].x, self[2].x),
            max(self[0].x, self[2].x),
        ])

    @property
    def y(self) -> Interval:
        return Interval([
            min(self[0].y, self[1].y),
            max(self[0].y, self[1].y),
        ])

    def intersects(self, obj: Any, inclusive: bool = True) -> bool:
        if isinstance(obj, Box):
            return (
                self.x.intersects(obj.x, inclusive=inclusive)
                and self.y.intersects(obj.y, inclusive=inclusive)
            )
        raise NotImplementedError(
            f"Box.intersects not implemented for {type(obj).__name__}"
        )

    def contains(self, obj: Any, inclusive: bool = True) -> bool:
        if isinstance(obj, Point):
            return (
                self.x.contains(obj.x, inclusive=inclusive)
                and self.y.contains(obj.y, inclusive=inclusive)
            )
        if isinstance(obj, Box):
            return (
                self.x.contains(obj.x, inclusive=inclusive)
                and self.y.contains(obj.y, inclusive=inclusive)
            )
        from attributes.segment import Segment
        if isinstance(obj, Segment):
            return (
                self.contains(obj[0], inclusive=inclusive)
                and self.contains(obj[1], inclusive=inclusive)
            )
        raise NotImplementedError(
            f"Box.contains not implemented for {type(obj).__name__}"
        )

    def __getitem__(self, index: int) -> Point:
        if index == 0:
            return self.bottom_left
        elif index == 1:
            return self.top_left
        elif index == 2:
            return self.bottom_right
        elif index == 3:
            return self.top_right
        raise IndexError("Box index out of range")
