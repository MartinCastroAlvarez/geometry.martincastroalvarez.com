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

from decimal import Decimal
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeAlias

from attributes import Signature
from exceptions import ValidationError
from geometry.point import Point
from geometry.point import SerializedPoint
from geometry.walk import Walk
from interfaces import Bounded
from interfaces import Serializable
from interfaces import Spatial

if TYPE_CHECKING:
    from geometry.box import Box

SerializedSegment: TypeAlias = list[SerializedPoint]


class Segment(list, Spatial, Bounded, Serializable[SerializedSegment]):
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
        from geometry.box import Box

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

        a: Point = self[0]
        b: Point = self[1]
        c: Point = obj[0]
        d: Point = obj[1]

        # Bounding-box rejection
        if (
            max(a.x, b.x) < min(c.x, d.x)
            or max(c.x, d.x) < min(a.x, b.x)
            or max(a.y, b.y) < min(c.y, d.y)
            or max(c.y, d.y) < min(a.y, b.y)
        ):
            return False

        w1 = Walk(start=a, center=b, end=c)
        w2 = Walk(start=a, center=b, end=d)
        w3 = Walk(start=c, center=d, end=a)
        w4 = Walk(start=c, center=d, end=b)

        col1 = w1.is_collinear()
        col2 = w2.is_collinear()
        col3 = w3.is_collinear()
        col4 = w4.is_collinear()

        # All-collinear case
        if col1 and col2 and col3 and col4:
            if not inclusive:
                return False

            # inclusive=True => any shared point
            if a.x != b.x or c.x != d.x:
                a0, a1 = sorted((a.x, b.x))
                b0, b1 = sorted((c.x, d.x))
            else:
                a0, a1 = sorted((a.y, b.y))
                b0, b1 = sorted((c.y, d.y))

            return not (a1 < b0 or b1 < a0)

        # Proper crossing
        if w1.orientation != w2.orientation and w3.orientation != w4.orientation:
            return True

        if not inclusive:
            return False

        # Inclusive non-collinear touching
        if col1 and self.contains(c, inclusive=True):
            return True
        if col2 and self.contains(d, inclusive=True):
            return True
        if col3 and obj.contains(a, inclusive=True):
            return True
        if col4 and obj.contains(b, inclusive=True):
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

    def serialize(self) -> SerializedSegment:
        return [self[0].serialize(), self[1].serialize()]

    @classmethod
    def unserialize(cls, data: SerializedSegment) -> Segment:
        if not isinstance(data, list) or len(data) != 2:
            raise ValidationError("Segment.unserialize expects a list of exactly 2 Point")
        return cls([Point.unserialize(data[0]), Point.unserialize(data[1])])
