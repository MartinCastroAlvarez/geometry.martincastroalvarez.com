from __future__ import annotations

from decimal import Decimal
from typing import Any

from art import ArtGallery
from convex import ConvexComponent
from designer import Drawable
from exceptions import ConsortiumCapacityTooLowError, PolygonTooFewPointsError
from guard import Guard
from model import Hash, Model, ModelMap
from obstacle import Obstacle
from point import Point, PointSequence
from polygon import Polygon
from triangle import Triangle
from visibility import Visibility


class Consortium(Model, Drawable):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        if all([len(args) == 1, isinstance(args[0], dict), not kwargs]):
            kwargs = args[0]
        if all(["polygon" in kwargs, not isinstance(kwargs["polygon"], Polygon)]):
            coords = kwargs["polygon"]
            if isinstance(coords, PointSequence):
                points = list(coords.items)
            elif isinstance(coords, list):
                points = [
                    (
                        point
                        if isinstance(point, Point)
                        else Point(
                            x=Decimal(str(float(point[0]))),
                            y=Decimal(str(float(point[1]))),
                        )
                    )
                    for point in coords
                ]
            else:
                points = []
            kwargs["polygon"] = Polygon(points=PointSequence(points))
        if "holes" in kwargs:
            raw_holes = kwargs["holes"]
            holes_list: list[Polygon] = []
            for hole in raw_holes:
                if isinstance(hole, Polygon):
                    holes_list.append(hole)
                else:
                    if isinstance(hole, PointSequence):
                        pts = list(hole.items)
                    elif isinstance(hole, list):
                        pts = [
                            (
                                point
                                if isinstance(point, Point)
                                else Point(
                                    x=Decimal(str(float(point[0]))),
                                    y=Decimal(str(float(point[1]))),
                                )
                            )
                            for point in hole
                        ]
                    else:
                        pts = []
                    holes_list.append(Polygon(points=PointSequence(pts)))
            kwargs["holes"] = ModelMap(items=[Obstacle(polygon=p) for p in holes_list])
        self.polygon = kwargs.get("polygon") or kwargs.get("boundary")
        self.holes: ModelMap[Obstacle] = (
            kwargs.get("holes") or kwargs.get("obstacles") or ModelMap(items=[])
        )
        if self.polygon is None:
            raise PolygonTooFewPointsError("Consortium requires polygon")
        capacity: int = int(kwargs.get("capacity", 0))
        if capacity < 10:
            raise ConsortiumCapacityTooLowError(
                f"Consortium capacity must be >= 10, got {capacity}"
            )
        self.capacity: int = capacity
        self.id = Hash(self)

        provisory_art_gallery = ArtGallery(polygon=self.polygon, holes=self.holes)

        self.galleries: ModelMap[ArtGallery] = ModelMap(items=[provisory_art_gallery])

    def __hash__(self) -> Hash:
        return Hash(f"{Hash(self.polygon)}:{Hash(self.holes)}")

    @property
    def boundary(self) -> Polygon:
        return self.polygon

    @property
    def obstacles(self) -> ModelMap[Obstacle]:
        return self.holes

    @property
    def points(self) -> PointSequence:
        return self.boundary.points

    @property
    def ears(self) -> list[Triangle]:
        return [ear for gallery in self.galleries.values() for ear in gallery.ears]

    @property
    def convex_components(self) -> ModelMap[ConvexComponent]:
        return ModelMap(
            items=[
                convex_component
                for gallery in self.galleries.values()
                for convex_component in gallery.convex_components
            ]
        )

    @property
    def guards(self) -> ModelMap[Guard]:
        return ModelMap(
            items=[
                guard for gallery in self.galleries.values() for guard in gallery.guards
            ]
        )

    @property
    def visibility(self) -> Visibility[Point]:
        return Visibility(
            items={
                guard.id: gallery.visibility[guard.id]
                for gallery in self.galleries.values()
                for guard in gallery.guards
            }
        )
