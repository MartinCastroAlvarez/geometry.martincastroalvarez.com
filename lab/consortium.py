from __future__ import annotations

from decimal import Decimal

from convex import ConvexComponent
from designer import Drawable
from guard import Guard
from model import ModelMap
from point import Point, PointSequence
from polygon import Polygon
from triangle import Triangle
from visibility import Visibility


class Consortium(Drawable):
    def __init__(self) -> None:
        self.polygon = Polygon(
            points=PointSequence(
                items=[
                    Point(x=Decimal("0"), y=Decimal("0")),
                    Point(x=Decimal("1"), y=Decimal("0")),
                    Point(x=Decimal("0"), y=Decimal("1")),
                ]
            )
        )
        self.holes = []

    @property
    def points(self) -> PointSequence:
        return PointSequence(items=[])

    @property
    def boundary(self) -> Polygon:
        return self.polygon

    @property
    def obstacles(self) -> list[Polygon]:
        return self.holes

    @property
    def ears(self) -> list[Triangle]:
        return []

    @property
    def convex_components(self) -> ModelMap[ConvexComponent]:
        return ModelMap(items=None)

    @property
    def guards(self) -> ModelMap[Guard]:
        return ModelMap(items=None)

    @property
    def visibility(self) -> Visibility[Point]:
        return Visibility()
