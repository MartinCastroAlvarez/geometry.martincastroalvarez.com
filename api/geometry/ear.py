"""
Ear: ConvexComponent with exactly 3 points and either is_ccw or is_cw. __and__ returns ConvexComponent.

Title
-----
Ear (Triangular Convex Component)

Context
-------
Ear is a triangle that is a valid ConvexComponent: exactly three points
and either counter-clockwise or clockwise (not collinear). Used in ear
clipping and decomposition. __and__(other) with Ear, ConvexComponent, or
Polygon wraps self and other as ConvexComponent and returns their shared
edge as ConvexComponent. Constructor raises ValidationError if not three
points or if collinear.

Examples:
>>> ear = Ear([p0, p1, p2])
>>> shared = ear & other_ear
"""

from __future__ import annotations

from exceptions import ValidationError
from geometry.convex import ConvexComponent
from geometry.point import Point
from geometry.polygon import Polygon
from geometry.polygon import SerializedPolygon
from geometry.segment import Segment
from structs import Sequence


class Ear(ConvexComponent):
    """
    A triangular ear: exactly 3 points, convex, and either counter-clockwise or clockwise.
    """

    def __init__(
        self,
        value: list[Point] | Sequence[Point] | None = None,
    ) -> None:
        super().__init__(value)
        if len(self) != 3:
            raise ValidationError("Ear must have exactly 3 points")
        if not self.is_ccw() and not self.is_cw():
            raise ValidationError("Ear must be either counter-clockwise or clockwise")

    @property
    def diagonal(self) -> Segment:
        """Chord opposite the ear tip (segment between first and last vertex)."""
        return self[0].to(self[2])

    def __and__(self, other: Ear | ConvexComponent | Polygon) -> ConvexComponent:
        """Wrap self and other as ConvexComponent and return their __and__ (always ConvexComponent)."""
        if not isinstance(other, (Ear, ConvexComponent, Polygon)):
            return NotImplemented
        self_cc = ConvexComponent(list(self))
        other_cc = ConvexComponent(list(other)) if isinstance(other, Ear) else other
        return self_cc & other_cc

    @classmethod
    def unserialize(cls, data: SerializedPolygon) -> Ear:
        """Build Ear from list of 3 point coords (each [x, y])."""
        return cls(list(Polygon.unserialize(data)))

    def __invert__(self) -> Ear:
        """Reverse the ear (swap start and end). CCW becomes CW, collinear stays collinear."""
        return Ear(list(reversed(self)))
