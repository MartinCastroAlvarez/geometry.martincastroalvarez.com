from __future__ import annotations

from decimal import Decimal

from element import Element
from model import Hash, Model
from point import PointSequence
from polygon import Polygon
from segment import SegmentSequence


class Obstacle(Model):
    def __init__(self, *, polygon: Polygon) -> None:
        super().__init__()
        if not isinstance(polygon, Polygon):
            raise TypeError(f"polygon must be a Polygon, got {type(polygon).__name__}")
        self.polygon = polygon
        self.id = Hash(f"obstacle:{self.polygon.__hash__()}")

    @property
    def points(self) -> PointSequence:
        return self.polygon.points

    @property
    def edges(self) -> SegmentSequence:
        return self.polygon.edges

    @property
    def signed_area(self) -> Decimal:
        return self.polygon.signed_area

    def contains(self, obj: Element, inclusive: bool = True) -> bool:
        return self.polygon.contains(obj, inclusive=inclusive)

    def intersects(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Obstacle):
            return self.polygon.intersects(obj.polygon, inclusive=inclusive)
        return self.polygon.intersects(obj, inclusive=inclusive)

    def __repr__(self) -> str:
        return f"Obstacle({self.polygon!r})"
