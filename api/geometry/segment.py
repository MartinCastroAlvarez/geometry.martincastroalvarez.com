"""
Segment type: exactly two Point (start, end). Spatial, Bounded. serialize/unserialize, midpoint, box, contains, intersects, crosses.

Title
-----
Segment (Line Segment)

Context
-------
Segment is a line segment between two Points. It implements Spatial
(contains, intersects), Bounded (box), and Serializable. size is
Euclidean length; midpoint is the center point; box is the axis-aligned
bounding box. contains(Point or Segment) and intersects(Segment) support
inclusive boundary. crosses(other) is True iff the segments cross at an
interior point (not touching at an endpoint or collinear overlap). Hash
is canonical (min point, max point). Used for polygon edges and
intersection tests in visibility and guard placement.

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

        # Bounding-box rejection
        if (
            max(self[0].x, self[1].x) < min(obj[0].x, obj[1].x)
            or max(obj[0].x, obj[1].x) < min(self[0].x, self[1].x)
            or max(self[0].y, self[1].y) < min(obj[0].y, obj[1].y)
            or max(obj[0].y, obj[1].y) < min(self[0].y, self[1].y)
        ):
            return False

        if self.crosses(obj):
            return True

        walk1: Walk = Walk(start=self[0], center=self[1], end=obj[0])
        walk2: Walk = Walk(start=self[0], center=self[1], end=obj[1])
        walk3: Walk = Walk(start=obj[0], center=obj[1], end=self[0])
        walk4: Walk = Walk(start=obj[0], center=obj[1], end=self[1])

        collinearity1: bool = walk1.is_collinear()
        collinearity2: bool = walk2.is_collinear()
        collinearity3: bool = walk3.is_collinear()
        collinearity4: bool = walk4.is_collinear()

        # All-collinear case
        if collinearity1 and collinearity2 and collinearity3 and collinearity4:
            if not inclusive:
                return False

            # inclusive=True => any shared point
            if self[0].x != self[1].x or obj[0].x != obj[1].x:
                a0, a1 = sorted((self[0].x, self[1].x))
                b0, b1 = sorted((obj[0].x, obj[1].x))
            else:
                a0, a1 = sorted((self[0].y, self[1].y))
                b0, b1 = sorted((obj[0].y, obj[1].y))

            return not (a1 < b0 or b1 < a0)

        if not inclusive:
            return False

        # Inclusive non-collinear touching
        if collinearity1 and self.contains(obj[0], inclusive=True):
            return True
        if collinearity2 and self.contains(obj[1], inclusive=True):
            return True
        if collinearity3 and obj.contains(self[0], inclusive=True):
            return True
        if collinearity4 and obj.contains(self[1], inclusive=True):
            return True

        return False

    def crosses(self, other: Segment) -> bool:
        """
        True iff this segment and other cross at a single point that is interior
        to both segments. Sharing an endpoint or collinear overlap is not a cross.
        """
        if not isinstance(other, Segment):
            raise NotImplementedError(f"Segment.crosses only supports Segment, got {type(other).__name__}")

        if (
            max(self[0].x, self[1].x) < min(other[0].x, other[1].x)
            or max(other[0].x, other[1].x) < min(self[0].x, self[1].x)
            or max(self[0].y, self[1].y) < min(other[0].y, other[1].y)
            or max(other[0].y, other[1].y) < min(self[0].y, self[1].y)
        ):
            return False

        if (
            self.contains(other[0], inclusive=True)
            or self.contains(other[1], inclusive=True)
            or other.contains(self[0], inclusive=True)
            or other.contains(self[1], inclusive=True)
        ):
            return False

        walk1: Walk = Walk(start=self[0], center=self[1], end=other[0])
        walk2: Walk = Walk(start=self[0], center=self[1], end=other[1])
        walk3: Walk = Walk(start=other[0], center=other[1], end=self[0])
        walk4: Walk = Walk(start=other[0], center=other[1], end=self[1])

        collinearity1: bool = walk1.is_collinear()
        collinearity2: bool = walk2.is_collinear()
        collinearity3: bool = walk3.is_collinear()
        collinearity4: bool = walk4.is_collinear()

        if collinearity1 and collinearity2 and collinearity3 and collinearity4:
            return False

        return walk1.orientation != walk2.orientation and walk3.orientation != walk4.orientation

    def touches(self, other: Segment) -> bool:
        """True iff this segment and other share at least one endpoint."""
        if not isinstance(other, Segment):
            raise NotImplementedError(f"Segment.touches only supports Segment, got {type(other).__name__}")
        return (
            self[0] == other[0]
            or self[0] == other[1]
            or self[1] == other[0]
            or self[1] == other[1]
        )

    def serialize(self) -> SerializedSegment:
        return [self[0].serialize(), self[1].serialize()]

    @classmethod
    def unserialize(cls, data: SerializedSegment) -> Segment:
        if not isinstance(data, list) or len(data) != 2:
            raise ValidationError("Segment.unserialize expects a list of exactly 2 Point")
        return cls([Point.unserialize(data[0]), Point.unserialize(data[1])])
