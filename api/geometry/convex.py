"""
ConvexComponent: Polygon that is convex (validated in constructor). __and__ returns ConvexComponent.

Title
-----
ConvexComponent (Convex Polygon)

Context
-------
ConvexComponent is a Polygon that is convex; the constructor validates
is_convex() for sequences of length >= 3 (two-point result from __and__
is allowed). __and__(other Polygon) returns the shared edge as a
ConvexComponent (two points). Used in art gallery decomposition after
ear clipping; visibility and guard placement operate on convex components.
Stored in ArtGallery.convex_components as Table[ConvexComponent].

Examples:
    cc = ConvexComponent([p0, p1, p2, p3])
    edge = cc & other_convex
"""

from __future__ import annotations

from exceptions import ValidationError
from geometry.point import Point
from geometry.polygon import Polygon


class ConvexComponent(Polygon):
    """
    A convex polygon. Validates is_convex() in constructor (skipped for 2-point edge result from __and__).
    """

    def __init__(
        self,
        value: list[Point] | None = None,
    ) -> None:
        super().__init__(value)
        if len(self) >= 3 and not self.is_convex():
            raise ValidationError("ConvexComponent must be convex")

    def __and__(self, other: Polygon) -> ConvexComponent:
        """Shared edge; returns ConvexComponent (2-point edge allowed)."""
        result: Polygon = super().__and__(other)
        return ConvexComponent(list(result))
