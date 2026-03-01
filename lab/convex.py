from __future__ import annotations

from typing import Any

from exceptions import ComponentMergeError
from exceptions import ComponentsNoSharedEdgeError
from exceptions import ConvexComponentInvalidPolygonError
from exceptions import ConvexComponentMergeTooManyPointsError
from exceptions import ConvexComponentNotConvexError
from model import Hash
from model import Model
from point import PointSequence
from polygon import Polygon
from segment import SegmentSequence
from serializable import Serializable


class ConvexComponent(Model, Serializable):
    def serialize(self) -> dict[str, Any]:
        return {"id": int(self.id), "polygon": self.polygon.serialize()}

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> ConvexComponent:
        if "polygon" not in data:
            raise ConvexComponentInvalidPolygonError("ConvexComponent.unserialize missing key 'polygon'")
        return cls(polygon=Polygon.unserialize(data["polygon"]))

    def __init__(self, *, polygon: Polygon) -> None:
        super().__init__()
        self.polygon = polygon
        self.validate()
        self.id = Hash(f"convex:{self.polygon.__hash__()}")

    def validate(self) -> None:
        if not isinstance(self.polygon, Polygon):
            raise ConvexComponentInvalidPolygonError(f"polygon must be a Polygon, got {type(self.polygon).__name__}")
        if not self.polygon.points.is_convex():
            raise ConvexComponentNotConvexError("Convex component must be convex.")

    @property
    def points(self) -> PointSequence:
        return self.polygon.points

    @property
    def edges(self) -> SegmentSequence:
        return self.polygon.points.edges

    def __repr__(self) -> str:
        return f"ConvexComponent({self.polygon!r})"

    def __add__(self, other: ConvexComponent) -> ConvexComponent:
        left = self.polygon.points
        right = other.polygon.points
        shared: PointSequence = left & right

        if len(shared) < 2:
            raise ComponentsNoSharedEdgeError("Components do not share a whole edge")
        if len(shared) > len(left):
            raise ConvexComponentMergeTooManyPointsError("Shared edge is too long")
        if len(shared) > len(right):
            raise ConvexComponentMergeTooManyPointsError("Shared edge is too long")

        print("  Merging Convex Components:")
        print(f"    Raw: {left} and {right}, with shared: {shared}")

        if shared not in right:
            right = ~right

        if shared not in left:
            left = ~left

        print(f"    Inverted: {left} and {right}, with shared: {shared}")

        left = left >> left.index(shared[-1])
        right = right << right.index(shared[0])

        print(f"    Shifted: {left} and {right}, with shared: {shared}")

        left = left[0 : len(left) - len(shared)]
        right = right[len(shared) :]

        print(f"    Sliced: {left} and {right}, with shared: {shared}")

        if shared in left:
            raise ComponentMergeError(f"{shared} is still in left {left}")

        if shared in right:
            raise ComponentMergeError(f"{shared} is still in right {right}")

        points: PointSequence = PointSequence(
            [
                *left.items,
                shared[0],
                *right.items,
                shared[-1],
            ]
        )

        print(f"    Merged: {points}")

        if len(points) < len(self.polygon) + len(other.polygon) - 2:
            raise ComponentMergeError("Failed to merge components")

        return ConvexComponent(polygon=Polygon(points=points))
