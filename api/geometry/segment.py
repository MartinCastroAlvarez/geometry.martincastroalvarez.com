"""
Segment type: exactly two Point (start, end). Spatial, Bounded. serialize/unserialize, midpoint, box, contains, intersects, connects.

Title
-----
Segment (Line Segment)

Context
-------
Segment is a line segment between two Points. It implements Spatial
(contains, intersects), Bounded (box), and Serializable. size is
Euclidean length; midpoint is the center point; box is the axis-aligned
bounding box. contains(Point or Segment) and intersects(Segment) support
inclusive boundary. connects(other) is True if the segments share an
endpoint. Hash is canonical (min point, max point). Used for polygon
edges and intersection tests in visibility and guard placement.

Examples:
>>> s = Segment([Point.unserialize(["0","0"]), Point.unserialize(["1","1"])])
>>> s.midpoint
>>> s.intersects(other_segment)
"""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from attributes.signature import Signature
from exceptions import ValidationError
from geometry.box import Box
from geometry.point import Point
from geometry.walk import Walk
from interfaces import Serializable
from interfaces.bounded import Bounded
from interfaces.spatial import Spatial


class Segment(list, Spatial, Bounded, Serializable[list[Any]]):
    """
    A segment as a list of exactly two Point (start, end). Validates in constructor.

    Example:
    >>> s = Segment([Point.unserialize(["0","0"]), Point.unserialize(["1","1"])])
    """

    def __init__(self, value: list[Point]) -> None:
        if value is None:
            raise ValidationError("Segment requires a list of exactly 2 Point, got None")
        if not isinstance(value, list):
            raise ValidationError(f"Segment must be a list of exactly 2 Point, got {type(value).__name__}")
        if len(value) == 0:
            raise ValidationError("Segment requires a list of exactly 2 Point, got empty list")
        if len(value) != 2:
            raise ValidationError(f"Segment must be a list of exactly 2 Point, got length {len(value)}")
        start, end = value[0], value[1]
        if not isinstance(start, Point):
            raise ValidationError(f"Segment start must be a Point, got {type(start).__name__}")
        if not isinstance(end, Point):
            raise ValidationError(f"Segment end must be a Point, got {type(end).__name__}")
        super().__init__([start, end])

    @property
    def start(self) -> Point:
        return list.__getitem__(self, 0)

    @property
    def end(self) -> Point:
        return list.__getitem__(self, 1)

    def __getitem__(self, index: int) -> Point:
        if index == 0:
            return list.__getitem__(self, 0)
        if index == 1:
            return list.__getitem__(self, 1)
        raise IndexError("Segment index out of range")

    def __hash__(self) -> Signature:
        low: Point = min(self[0], self[1])
        high: Point = max(self[0], self[1])
        return Signature(f"segment:{low.x}:{low.y}:{high.x}:{high.y}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Segment):
            return False
        return any(
            (
                self[0] == other[0] and self[1] == other[1],
                self[0] == other[1] and self[1] == other[0],
            )
        )

    def __invert__(self) -> Segment:
        return Segment([self[1], self[0]])

    @property
    def size(self) -> Decimal:
        """Euclidean distance between start and end: sqrt((dx^2 + dy^2))."""
        dx: Decimal = self[1].x - self[0].x
        dy: Decimal = self[1].y - self[0].y
        return (dx * dx + dy * dy).sqrt()

    @property
    def midpoint(self) -> Point:
        return Point(
            (
                (self[0].x + self[1].x) / 2,
                (self[0].y + self[1].y) / 2,
            )
        )

    @property
    def box(self) -> Box:
        min_x = min(self[0].x, self[1].x)
        max_x = max(self[0].x, self[1].x)
        min_y = min(self[0].y, self[1].y)
        max_y = max(self[0].y, self[1].y)
        return Box(
            bottom_left=Point((min_x, min_y)),
            top_left=Point((min_x, max_y)),
            bottom_right=Point((max_x, min_y)),
            top_right=Point((max_x, max_y)),
        )

    def contains(self, obj: Any, inclusive: bool = True) -> bool:
        if isinstance(obj, Point):
            return all(
                (
                    Walk(start=self[0], center=self[1], end=obj).is_collinear(),
                    self.box.contains(obj, inclusive=inclusive),
                )
            )
        if isinstance(obj, Segment):
            return all(
                (
                    self.contains(obj[0], inclusive=inclusive),
                    self.contains(obj[1], inclusive=inclusive),
                )
            )
        raise NotImplementedError(f"Segment.contains only supports Point or Segment, got {type(obj).__name__}")

    def intersects(self, obj: Any, inclusive: bool = True) -> bool:
        if not isinstance(obj, Segment):
            raise NotImplementedError(f"Segment.intersects only supports Segment, got {type(obj).__name__}")
        other = obj
        if any(
            (
                self.box.x[1] < other.box.x[0],
                other.box.x[1] < self.box.x[0],
                self.box.y[1] < other.box.y[0],
                other.box.y[1] < self.box.y[0],
            )
        ):
            return False
        path1 = Walk(start=self[0], center=self[1], end=other[0])
        path2 = Walk(start=self[0], center=self[1], end=other[1])
        path3 = Walk(start=other[0], center=other[1], end=self[0])
        path4 = Walk(start=other[0], center=other[1], end=self[1])
        if all(
            (
                all(
                    (
                        not path1.is_collinear(),
                        not path2.is_collinear(),
                        not path3.is_collinear(),
                        not path4.is_collinear(),
                    )
                ),
                path1.orientation != path2.orientation,
                path3.orientation != path4.orientation,
            )
        ):
            return True
        if any(
            (
                path1.is_collinear() and self.contains(other[0], inclusive=inclusive),
                path2.is_collinear() and self.contains(other[1], inclusive=inclusive),
                path3.is_collinear() and other.contains(self[0], inclusive=inclusive),
                path4.is_collinear() and other.contains(self[1], inclusive=inclusive),
            )
        ):
            return True
        return False

    def connects(self, other: Segment) -> bool:
        return any(
            (
                self[0] == other[0],
                self[0] == other[1],
                self[1] == other[0],
                self[1] == other[1],
            )
        )

    def serialize(self) -> list[list[Any]]:
        return [json.loads(self[0].serialize()), json.loads(self[1].serialize())]

    @classmethod
    def unserialize(cls, data: list[Any]) -> Segment:
        if not isinstance(data, list) or len(data) != 2:
            raise ValidationError("Segment.unserialize expects a list of exactly 2 Point")
        return cls([Point.unserialize(data[0]), Point.unserialize(data[1])])
