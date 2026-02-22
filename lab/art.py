from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from functools import cached_property
from typing import Any
from uuid import UUID

from convex import ConvexComponent
from element import Element, Element2D
from exceptions import (BridgeFailureError,
                        ComponentsEmptyOutsideBoundaryError,
                        ComponentsNoSharedEdgeError,
                        ConvexComponentNotCCWError,
                        ConvexComponentNotConvexError, EarClippingFailureError,
                        GuardCoverageFailureError, PolygonDegenerateError,
                        PolygonNotSimpleError, PolygonTooFewPointsError,
                        StitchWinnerSubsequenceError)
from guard import VertexGuard
from model import ModelMap
from path import Path
from point import Point, PointSequence
from polygon import Polygon
from segment import Segment, SegmentSequence
from triangle import Triangle
from visibility import Visibility


class ArtGallery(Element2D):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and isinstance(args[0], dict) and not kwargs:
            kwargs = args[0]
        if "polygon" in kwargs and not isinstance(kwargs["polygon"], Polygon):
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
            holes_list = []
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
            kwargs["holes"] = holes_list
        self.polygon = kwargs.get("polygon")
        self.holes = kwargs.get("holes", [])
        self._visibility_cache: dict[Segment, bool] = {}
        if self.polygon is None:
            raise PolygonTooFewPointsError("ArtGallery requires polygon")
        boundary: SegmentSequence = self.polygon.edges
        for i, hole in enumerate(self.holes):
            if not all(
                self.polygon.contains(point, inclusive=False) for point in hole.points
            ):
                raise PolygonNotSimpleError(
                    f"Hole {i} is not strictly inside the boundary (outside or touching boundary)."
                )
            for edge in hole.edges:
                for boundary_edge in boundary:
                    if edge.intersects(
                        boundary_edge, inclusive=True
                    ) and not edge.connects(boundary_edge):
                        raise PolygonNotSimpleError(
                            f"Hole {i} intersects/touches boundary."
                        )
            for point in hole.points:
                for boundary_edge in boundary:
                    if boundary_edge.contains(point, inclusive=True):
                        raise PolygonNotSimpleError(
                            f"Hole {i} has a vertex on the boundary."
                        )
        for i, hole in enumerate(self.holes):
            for other in self.holes[i + 1 :]:
                if hole.overlaps(other, inclusive=True):
                    raise PolygonNotSimpleError("Holes intersect or touch.")

    def __repr__(self) -> str:
        lines: list[str] = ["Art Gallery perimeter:"]
        for i, point in enumerate(self.polygon.points):
            lines.append(f" Vertex {i}: {point}")
        for hole_idx, hole in enumerate(self.holes):
            lines.append(f"Hole {hole_idx}:")
            for i, point in enumerate(hole.points):
                lines.append(f" Vertex {i}: {point}")
        return "\n".join(lines)

    @cached_property
    def signed_area(self) -> Decimal:
        return self.polygon.signed_area - sum(
            abs(hole.signed_area) for hole in self.holes
        )

    @cached_property
    def points(self) -> PointSequence:
        points: PointSequence = self.polygon.points
        if not self.holes:
            return points
        print(f"Stitching {len(self.holes)} holes to {len(points)} points.")
        holes: list[Polygon] = sorted(
            self.holes,
            key=lambda hole: (
                hole.points.rightmost[0],
                hole.points.rightmost[1],
            ),
            reverse=True,
        )
        edges: SegmentSequence = points.edges
        for hole_idx, hole in enumerate(holes):
            hole_points = hole.points if hole.points.is_cw() else ~hole.points
            anchor: Point = hole_points.rightmost
            print(f"  Hole {hole_idx}: Briding {hole.points} to {points}")
            bridge: Segment | None = None
            for candidate in points:
                if candidate == anchor:
                    continue
                if candidate[0] < anchor[0]:
                    continue
                if candidate[1] < anchor[1]:
                    continue
                segment: Segment = candidate.to(anchor)
                if not self.polygon.contains(segment, inclusive=True):
                    continue
                if any(
                    Path(start=edge[0], center=edge[1], end=segment[0]).is_collinear()
                    and Path(
                        start=edge[0], center=edge[1], end=segment[1]
                    ).is_collinear()
                    for edge in self.polygon.edges
                    if not edge.connects(segment)
                ):
                    continue
                if any(
                    other_hole.overlaps(segment, inclusive=False)
                    for other_hole in self.holes
                    if other_hole is not hole
                ):
                    continue
                if any(
                    edge.intersects(segment)
                    for edge in edges
                    if not edge.connects(segment)
                ):
                    continue
                if bridge is None or segment.size < bridge.size:
                    bridge = segment

            if bridge is None:
                print(f"  Hole {hole_idx}: no valid bridge found for anchor {anchor}.")
                raise BridgeFailureError(
                    f"No valid bridge found for hole: {hole.points}"
                )

            winner: Segment = bridge
            vertex: Point = winner[0]

            print(f"  Hole {hole_idx}: Stitching {bridge}")
            print(f"    Hole {hole_points}")
            print(f"    Anchor {anchor}")
            print(f"    Vertex {vertex}")
            print(f"    Points {points}")

            if winner in points:
                raise StitchWinnerSubsequenceError(
                    f"Winner {winner} is a subsequence of boundary points; cannot stitch"
                )

            if winner in hole_points:
                raise StitchWinnerSubsequenceError(
                    f"Winner {winner} is a subsequence of hole {hole_idx}; cannot stitch"
                )

            left = points >> vertex
            right = hole_points << anchor

            if not left.is_ccw():
                raise Exception(f"Left {left} is not CCW; cannot stitch")
            if not right.is_cw():
                raise Exception(f"Right {right} is not CW; cannot stitch")

            points = PointSequence(
                [
                    *left.items,
                    *right.items,
                    anchor,
                    vertex,
                ]
            )
            edges = points.edges
            print(f"    Stitched: {len(points)} points: {points}.")

        if not points.is_ccw():
            points = ~points
            print("  Stitched polygon was CW; reversed to CCW.")
        return points

    def sees(self, source: Point, target: Point | ConvexComponent) -> bool:
        if isinstance(target, ConvexComponent):
            return all(self.sees(source, point) for point in target.polygon.points)
        if source == target:
            return True
        segment: Segment = source.to(target)
        if segment in self._visibility_cache:
            return self._visibility_cache[segment]
        if not self.contains(segment, inclusive=True):
            self._visibility_cache[segment] = False
            return False

        obstacles: list[Segment] = list(self.polygon.edges)
        for hole in self.holes:
            obstacles.extend(hole.edges)
        for edge in obstacles:
            if edge.connects(segment):
                continue
            if not edge.intersects(segment, inclusive=False):
                continue
            path1 = Path(start=edge[0], center=edge[1], end=segment[0])
            path2 = Path(start=edge[0], center=edge[1], end=segment[1])
            if path1.is_collinear() or path2.is_collinear():
                continue
            self._visibility_cache[segment] = False
            return False
        self._visibility_cache[segment] = True
        return True

    @cached_property
    def ears(self) -> list[Triangle]:
        points: PointSequence = self.points
        print(f"Ear clipping - {len(points)} points: {points}.")
        ears: list[Triangle] = []
        while len(points) > 3:
            titanic: Polygon = Polygon(points=points)
            n = len(points)
            i: int | None = None
            for j in range(n):
                ear = Triangle(
                    left=points[j - 1],
                    center=points[j],
                    right=points[j + 1],
                )
                print(f"  Ear {ear}")
                if ear.path.is_collinear():
                    continue
                if not ear.path.is_ccw():
                    print(f"  Ear {ear} is not convex at the middle point; skipping.")
                    continue
                if not titanic.contains(ear.diagonal, inclusive=True):
                    print(f"  Ear {ear} is not inside the art gallery; skipping.")
                    continue
                if any(
                    ear.contains(points[k], inclusive=False)
                    for k in range(n)
                    if k not in ((j - 1) % n, j, (j + 1) % n)
                ):
                    print(f"  Ear {ear} contains a point; skipping.")
                    continue
                i = j
                ears.append(ear)
                break
            if i is None:
                raise EarClippingFailureError(
                    f"Ear clipping failed: No ear found for: {points}"
                )
            points = points.pop(i)
        if len(points) < 3:
            raise PolygonTooFewPointsError("ArtGallery must have at least 3 points")
        path = Path(start=points[0], center=points[1], end=points[2])
        if path.is_collinear():
            pass
        elif path.is_ccw():
            ears.append(Triangle(left=points[0], center=points[1], right=points[2]))
        else:
            ears.append(Triangle(left=points[2], center=points[1], right=points[0]))
        print(f"Ear clipping done - {len(ears)} ears found.")
        for ear in ears:
            print(f"  {ear}")
        return ears

    @cached_property
    def convex_components(self) -> ModelMap[ConvexComponent]:
        components: ModelMap[ConvexComponent] = ModelMap(
            items=[ConvexComponent(polygon=ear.polygon) for ear in self.ears]
        )
        while True:
            components_by_edge: defaultdict[Segment, list[UUID]] = defaultdict(list)
            for component in components.values():
                for edge in component.polygon.edges:
                    components_by_edge[edge].append(component.id)
            best_area: Decimal | None = None
            best_component: ConvexComponent | None = None
            best_pair: tuple[ConvexComponent, ConvexComponent] | None = None
            for component in components.values():
                adjacent = {
                    other_id
                    for edge in component.polygon.edges
                    for other_id in components_by_edge[edge]
                    if other_id != component.id
                }
                for other_id in adjacent:
                    try:
                        merged = component + components[other_id]
                    except (
                        ComponentsEmptyOutsideBoundaryError,
                        ComponentsNoSharedEdgeError,
                        ConvexComponentNotCCWError,
                        ConvexComponentNotConvexError,
                        PolygonTooFewPointsError,
                        PolygonNotSimpleError,
                        PolygonDegenerateError,
                    ) as error:
                        print(
                            f"  Merging {component} and {components[other_id]} failed: {type(error)}: {error}"
                        )
                        continue
                    if best_area is None or abs(merged.polygon) > best_area:
                        best_area = abs(merged.polygon)
                        best_component = merged
                        best_pair = (component, components[other_id])
            if best_pair is None:
                break
            components.pop(best_pair[0].id)
            components.pop(best_pair[1].id)
            components.add(best_component)
            print(f"  Merged two components -> {len(components)} remaining.")
        print(f"Convex components: {len(components)}.")
        return components

    @cached_property
    def guards(self) -> ModelMap[VertexGuard]:
        components: ModelMap[ConvexComponent] = self.convex_components.clone()
        points: set[Point] = {
            point
            for component in components.values()
            for point in component.polygon.points
        }
        candidates: ModelMap[VertexGuard] = ModelMap(
            items=[VertexGuard(position=point) for point in points]
        )
        guards: ModelMap[VertexGuard] = ModelMap(items=[])
        while components:
            visibility_by_guard: Visibility[UUID] = Visibility()
            for guard in candidates.values():
                visibility_by_guard[guard.id] = {
                    component.id
                    for component in components.values()
                    if self.sees(guard.position, component)
                }
            best_guard_id: UUID = visibility_by_guard.best
            best_guard: VertexGuard = candidates[best_guard_id]
            covered: int = len(visibility_by_guard[best_guard.id])
            guards.add(best_guard)
            candidates.pop(best_guard.id)
            for component_id in visibility_by_guard[best_guard.id]:
                components.pop(component_id)
            print(
                f"  {best_guard}: covers {covered} component(s), {len(components)} remaining.",
            )
        if components:
            print("Guards: failed to cover all convex components.")
            raise GuardCoverageFailureError("Failed to cover all convex components.")
        print(f"Guards: {len(guards)} guard(s) placed.")

        removed = True
        while removed:
            removed = False
            visibility_by_guard: Visibility[UUID] = Visibility()
            for guard in guards.values():
                visibility_by_guard[guard.id] = {
                    point for point in self.points if self.sees(guard.position, point)
                }
            if not all(visibility_by_guard.sees(point) for point in self.points):
                raise GuardCoverageFailureError("Failed to cover all points.")
            for guard in list(guards.values()):
                guard_points: set[Point] = visibility_by_guard[guard.id]
                other_points: set[Point] = {
                    point
                    for other in guards.values()
                    if other.id != guard.id
                    for point in visibility_by_guard[other.id]
                    if point in guard_points
                }
                if guard_points <= other_points:
                    print(
                        f"  Guard ({guard.position[0]}, {guard.position[1]}): pruned."
                    )
                    for point in guard_points:
                        for viewer_id in visibility_by_guard.sees(point):
                            viewer = guards[viewer_id]
                            print(f"  {viewer} sees point {point}.")

                    guards.pop(guard.id)
                    removed = True
                    break
        return guards

    @cached_property
    def visibility(self) -> Visibility[Point]:
        vis: Visibility[Point] = Visibility()
        for guard in self.guards.values():
            vis[guard.id] = {
                point for point in self.points if self.sees(guard.position, point)
            }
        return vis

    def contains(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Point):
            if not self.polygon.contains(obj, inclusive=inclusive):
                return False
            return not any(hole.contains(obj, inclusive=False) for hole in self.holes)

        if isinstance(obj, Segment):
            if not self.polygon.contains(obj, inclusive=inclusive):
                return False
            if any(
                hole.contains(obj[0], inclusive=False)
                or hole.contains(obj[1], inclusive=False)
                for hole in self.holes
            ):
                return False
            if any(hole.contains(obj.midpoint, inclusive=False) for hole in self.holes):
                return False
            if not self.contains(obj.midpoint, inclusive=inclusive):
                return False

            # gartlar
            for hole in self.holes:
                for edge in hole.edges:
                    if edge.connects(obj):
                        continue
                    # strict intersection only (inclusive=False) so touching endpoints is allowed
                    if not edge.intersects(obj, inclusive=False):
                        continue
                    # allow collinear "lying on boundary" cases
                    if (
                        Path(start=edge[0], center=edge[1], end=obj[0]).is_collinear()
                        or Path(
                            start=edge[0], center=edge[1], end=obj[1]
                        ).is_collinear()
                    ):
                        continue
                    return False

            return True

        if isinstance(obj, Polygon):
            return all(
                (
                    all(self.contains(edge, inclusive=inclusive) for edge in obj.edges),
                    all(
                        self.contains(point, inclusive=inclusive)
                        for point in obj.points
                    ),
                )
            )

        raise NotImplementedError(
            f"ArtGallery.contains not implemented for {type(obj)}"
        )

    def overlaps(self, obj: Element, inclusive: bool = True) -> bool:
        return all(
            [
                self.polygon.overlaps(obj, inclusive=inclusive),
                not any(hole.contains(obj, inclusive=False) for hole in self.holes),
            ]
        )
