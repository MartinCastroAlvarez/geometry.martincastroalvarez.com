"""
Ear: ConvexComponent with exactly 3 points and either is_ccw or is_cw. __and__ returns ConvexComponent.
"""

from __future__ import annotations

from exceptions import ValidationError

from geometry.convex import ConvexComponent
from geometry.point import Point
from geometry.polygon import Polygon


class Ear(ConvexComponent):
    """
    A triangular ear: exactly 3 points, convex, and either counter-clockwise or clockwise.
    """

    def __init__(
        self,
        value: list[Point] | None = None,
    ) -> None:
        super().__init__(value)
        if len(self) != 3:
            raise ValidationError("Ear must have exactly 3 points")
        if not self.is_ccw() and not self.is_cw():
            raise ValidationError("Ear must be either counter-clockwise or clockwise")

    def __and__(self, other: Ear | ConvexComponent | Polygon) -> ConvexComponent:
        """Wrap self and other as ConvexComponent and return their __and__ (always ConvexComponent)."""
        if not isinstance(other, (Ear, ConvexComponent, Polygon)):
            return NotImplemented
        self_cc = ConvexComponent(list(self))
        other_cc = ConvexComponent(list(other)) if isinstance(other, Ear) else other
        return self_cc & other_cc
