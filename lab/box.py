from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from element import ComplexElement, Element
from exceptions import BoxInvalidEdgeError
from interval import Interval
from point import Point


class Bounded(ABC):
    @property
    @abstractmethod
    def box(self) -> Box:
        raise NotImplementedError()


class Box(ComplexElement):
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
        if self.bottom_left[0] != self.top_left[0]:
            raise BoxInvalidEdgeError(
                f"Box must have vertical left edge: {self.bottom_left[0]} != {self.top_left[0]}"
            )
        if self.bottom_right[0] != self.top_right[0]:
            raise BoxInvalidEdgeError(
                f"Box must have vertical right edge: {self.bottom_right[0]} != {self.top_right[0]}"
            )
        if self.bottom_left[1] != self.bottom_right[1]:
            raise BoxInvalidEdgeError(
                f"Box must have horizontal bottom edge: {self.bottom_left[1]} != {self.bottom_right[1]}"
            )
        if self.top_left[1] != self.top_right[1]:
            raise BoxInvalidEdgeError(
                f"Box must have horizontal top edge: {self.top_left[1]} != {self.top_right[1]}"
            )

    @property
    def x(self) -> Interval:
        return Interval(
            start=min(self[0][0], self[2][0]), end=max(self[0][0], self[2][0])
        )

    @property
    def y(self) -> Interval:
        return Interval(
            start=min(self[0][1], self[1][1]), end=max(self[0][1], self[1][1])
        )

    def overlaps(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Box):
            return all(
                (
                    self.x.overlaps(obj.x, inclusive=inclusive),
                    self.y.overlaps(obj.y, inclusive=inclusive),
                )
            )

        raise NotImplementedError(f"Box.overlaps not implemented for {type(obj)}")

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
