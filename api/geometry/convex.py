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
>>> cc = ConvexComponent([p0, p1, p2, p3])
>>> edge = cc & other_convex
"""

from __future__ import annotations

from attributes import Signature
from exceptions import ValidationError
from geometry.point import Point
from geometry.polygon import Polygon
from geometry.polygon import SerializedPolygon
from structs import Sequence


class ConvexComponent(Polygon):
    """
    A convex polygon. Validates is_convex() in constructor (skipped for 2-point edge result from __and__).
    """

    def __hash__(self) -> Signature:
        return super().__hash__()

    def __init__(
        self,
        value: list[Point] | Sequence[Point] | None = None,
    ) -> None:
        super().__init__(value)
        if len(self) >= 3 and not self.is_convex():
            raise ValidationError("ConvexComponent must be convex")

    def __and__(self, other: Polygon) -> ConvexComponent:
        """Shared edge; returns ConvexComponent (2-point edge allowed)."""
        result: Polygon = super().__and__(other)
        return ConvexComponent(list(result))

    def __add__(self, other: ConvexComponent) -> ConvexComponent:
        """Merge with other along shared edge; returns new ConvexComponent."""
        shared: Polygon = super().__and__(other)
        a: Point = shared[0]
        b: Point = shared[1]
        n_self: int = len(self)
        n_other: int = len(other)
        left: Polygon
        for i in range(n_self):
            if self[i] == a and self[(i + 1) % n_self] == b:
                left = Polygon(list(Sequence(list(self)) >> (i + 1)))
                break
        else:
            self_rev: Polygon = Polygon(list(reversed(self)))
            for i in range(n_self):
                if self_rev[i] == a and self_rev[(i + 1) % n_self] == b:
                    left = Polygon(list(Sequence(list(self_rev)) >> (i + 1)))
                    break
            else:
                raise ValidationError("ConvexComponent merge: shared edge not found in self")
        right: Polygon
        for j in range(n_other):
            if other[j] == a and other[(j + 1) % n_other] == b:
                right = Polygon(list(Sequence(list(other)) << j))
                break
        else:
            other_rev: Polygon = Polygon(list(reversed(other)))
            for j in range(n_other):
                if other_rev[j] == a and other_rev[(j + 1) % n_other] == b:
                    right = Polygon(list(Sequence(list(other_rev)) << j))
                    break
            else:
                raise ValidationError("ConvexComponent merge: shared edge not found in other")
        merged: list[Point] = list(left)[:-2] + [a] + list(right)[2:] + [b]
        return ConvexComponent(list(Sequence(merged)))

    @classmethod
    def unserialize(cls, data: SerializedPolygon) -> ConvexComponent:
        """Build ConvexComponent from list of point coords (each [x, y])."""
        return cls(list(Polygon.unserialize(data)))
