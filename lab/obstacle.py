from __future__ import annotations

from decimal import Decimal
from typing import Any

from element import Element
from model import Hash, Model
from point import PointSequence
from polygon import Polygon
from segment import SegmentSequence
from serializable import Serializable


class Obstacle(Model, Serializable):
    def serialize(self) -> dict[str, Any]:
        return {"id": int(self.id), "polygon": self.polygon.serialize()}

    @classmethod
    def unserialize(cls, data: dict[str, Any] | list[Any]) -> Obstacle:
        polygon_data = (
            data["polygon"] if isinstance(data, dict) and "polygon" in data else data
        )
        return cls(polygon=Polygon.unserialize(polygon_data))

    def __init__(self, *, polygon: Polygon) -> None:
        super().__init__()
        self.polygon = polygon
        self.validate()
        self.id = Hash(f"obstacle:{self.polygon.__hash__()}")

    def validate(self) -> None:
        if not isinstance(self.polygon, Polygon):
            raise TypeError(
                f"polygon must be a Polygon, got {type(self.polygon).__name__}"
            )

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
