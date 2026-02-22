from __future__ import annotations

from exceptions import (ComponentMergeError, ComponentsNoSharedEdgeError,
                        ConvexComponentInvalidPolygonError,
                        ConvexComponentMergeTooManyPointsError,
                        ConvexComponentNotConvexError)
from model import Model
from point import PointSequence
from polygon import Polygon


class ConvexComponent(Model):
    def __init__(self, *, polygon: Polygon) -> None:
        super().__init__()
        if not isinstance(polygon, Polygon):
            raise ConvexComponentInvalidPolygonError(
                f"polygon must be a Polygon, got {type(polygon).__name__}"
            )
        self.polygon = polygon
        if not self.polygon.points.is_convex():
            raise ConvexComponentNotConvexError("Convex component must be convex.")

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

        if not right.contains(shared):
            right = ~right

        if not left.contains(shared):
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
