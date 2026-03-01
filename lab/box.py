from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from element import ComplexElement
from element import Element
from exceptions import BoxInvalidEdgeError
from exceptions import SerializedInvalidDictError
from interval import Interval
from point import Point
from serializable import Serializable


class Bounded(ABC):
    @property
    @abstractmethod
    def box(self) -> Box:
        raise NotImplementedError()


class Box(ComplexElement, Serializable):
    def serialize(self) -> dict[str, Any]:
        return {
            "bottom_left": self.bottom_left.serialize(),
            "top_left": self.top_left.serialize(),
            "bottom_right": self.bottom_right.serialize(),
            "top_right": self.top_right.serialize(),
            "x": self.x.serialize(),
            "y": self.y.serialize(),
        }

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> Box:
        if not isinstance(data, dict):
            raise SerializedInvalidDictError(f"Box.unserialize expects a dict, got {type(data).__name__}")
        for key in ("bottom_left", "top_left", "bottom_right", "top_right"):
            if key not in data:
                raise BoxInvalidEdgeError(f"Box.unserialize missing key {key!r}")
        return cls(
            bottom_left=Point.unserialize(data["bottom_left"]),
            top_left=Point.unserialize(data["top_left"]),
            bottom_right=Point.unserialize(data["bottom_right"]),
            top_right=Point.unserialize(data["top_right"]),
        )

    def __init__(
        self,
        *,
        bottom_left: Any,
        top_left: Any,
        bottom_right: Any,
        top_right: Any,
    ) -> None:
        self.bottom_left = bottom_left if isinstance(bottom_left, Point) else Point(bottom_left)
        self.top_left = top_left if isinstance(top_left, Point) else Point(top_left)
        self.bottom_right = bottom_right if isinstance(bottom_right, Point) else Point(bottom_right)
        self.top_right = top_right if isinstance(top_right, Point) else Point(top_right)
        self.validate()

    def validate(self) -> None:
        if self.bottom_left[0] != self.top_left[0]:
            raise BoxInvalidEdgeError(f"Box must have vertical left edge: {self.bottom_left[0]} != {self.top_left[0]}")
        if self.bottom_right[0] != self.top_right[0]:
            raise BoxInvalidEdgeError(f"Box must have vertical right edge: {self.bottom_right[0]} != {self.top_right[0]}")
        if self.bottom_left[1] != self.bottom_right[1]:
            raise BoxInvalidEdgeError(f"Box must have horizontal bottom edge: {self.bottom_left[1]} != {self.bottom_right[1]}")
        if self.top_left[1] != self.top_right[1]:
            raise BoxInvalidEdgeError(f"Box must have horizontal top edge: {self.top_left[1]} != {self.top_right[1]}")

    @property
    def x(self) -> Interval:
        return Interval(start=min(self[0][0], self[2][0]), end=max(self[0][0], self[2][0]))

    @property
    def y(self) -> Interval:
        return Interval(start=min(self[0][1], self[1][1]), end=max(self[0][1], self[1][1]))

    def intersects(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Box):
            return all(
                (
                    self.x.intersects(obj.x, inclusive=inclusive),
                    self.y.intersects(obj.y, inclusive=inclusive),
                )
            )

        raise NotImplementedError(f"Box.intersects not implemented for {type(obj)}")

    def contains(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Point):
            return all(
                (
                    self.x.contains(obj[0], inclusive=inclusive),
                    self.y.contains(obj[1], inclusive=inclusive),
                )
            )

        if isinstance(obj, Box):
            return all(
                (
                    self.x.contains(obj.x, inclusive=inclusive),
                    self.y.contains(obj.y, inclusive=inclusive),
                )
            )

        from segment import Segment
        from triangle import Triangle

        if isinstance(obj, Segment):
            return all(
                (
                    self.contains(obj[0], inclusive=inclusive),
                    self.contains(obj[1], inclusive=inclusive),
                )
            )

        if isinstance(obj, Triangle):
            return all(
                (
                    self.contains(obj[0], inclusive=inclusive),
                    self.contains(obj[1], inclusive=inclusive),
                    self.contains(obj[2], inclusive=inclusive),
                )
            )

        raise NotImplementedError(f"Box.contains not implemented for {type(obj)}")

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
