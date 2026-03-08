"""
State classes for step persistence.

Title
-----
States Module

Context
-------
Each State subclass corresponds to a Step subclass and holds intermediate
state that can be persisted across retries or restarts. State is serializable
to dict for persistence via JobStateRepository.

Examples:
>>> from states import GuardPlacementStepState
>>> state = GuardPlacementStepState()
>>> state.serialize()
{...}
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from typing import Any

from attributes import Identifier
from geometry import ConvexComponent
from geometry import Ear
from geometry import Point
from geometry import Polygon
from geometry import Segment
from structs import Collection
from structs import Table


class State(ABC):
    """
    Abstract base for step state. State is serializable to dict.
    """

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        """Serialize the state to a dict for persistence."""
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def unserialize(cls, data: dict[str, Any]) -> "State":
        """Unserialize the state from a dict."""
        raise NotImplementedError


class ArtGalleryStepState(State):
    """State for ArtGalleryStep. Has no additional attributes."""

    def serialize(self) -> dict[str, Any]:
        return {}

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "ArtGalleryStepState":
        return cls()


class ValidationPolygonStepState(State):
    """State for ValidationPolygonStep. Has no additional attributes."""

    def serialize(self) -> dict[str, Any]:
        return {}

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "ValidationPolygonStepState":
        return cls()


class StitchingStepState(State):
    """
    State for StitchingStep. Has points (Polygon), stitches, and remaining_obstacles (list of Polygon).
    Gallery is read-only; always read/write via state.
    """

    points: Polygon
    stitches: list[Segment]
    remaining_obstacles: list[Polygon]

    def __init__(
        self,
        points: Polygon | None = None,
        stitches: list[Segment] | None = None,
        remaining_obstacles: list[Polygon] | None = None,
    ) -> None:
        self.points = points if points is not None else Polygon([])
        self.stitches = stitches if stitches is not None else []
        self.remaining_obstacles = remaining_obstacles if remaining_obstacles is not None else []

    def serialize(self) -> dict[str, Any]:
        return {
            "points": self.points.serialize(),
            "stitches": [s.serialize() for s in self.stitches],
            "remaining_obstacles": [p.serialize() for p in self.remaining_obstacles],
        }

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "StitchingStepState":
        points_raw = data.get("points") or []
        points = Polygon.unserialize(points_raw) if points_raw else Polygon([])
        stitches_raw = data.get("stitches") or []
        stitches = [Segment.unserialize(s) for s in stitches_raw]
        obstacles_raw = data.get("remaining_obstacles") or []
        remaining_obstacles = [Polygon.unserialize(p) for p in obstacles_raw]
        return cls(points=points, stitches=stitches, remaining_obstacles=remaining_obstacles)


class EarClippingStepState(State):
    """State for EarClippingStep. Has titanic (Polygon, remaining to clip), splits (list of Polygon), and ears (Table). Gallery is read-only."""

    titanic: Polygon
    splits: list[Polygon]
    ears: Table

    def __init__(
        self,
        titanic: Polygon | None = None,
        splits: list[Polygon] | None = None,
        ears: Table | None = None,
    ) -> None:
        self.titanic = titanic if titanic is not None else Polygon([])
        self.splits = splits if splits is not None else []
        self.ears = ears if ears is not None else Table()

    def serialize(self) -> dict[str, Any]:
        return {
            "titanic": self.titanic.serialize(),
            "splits": [p.serialize() for p in self.splits],
            "ears": self.ears.serialize(),
        }

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "EarClippingStepState":
        titanic_raw = data.get("titanic") or []
        titanic = Polygon.unserialize(titanic_raw) if titanic_raw else Polygon([])
        splits_raw = data.get("splits") or []
        splits = [Polygon.unserialize(p) for p in splits_raw]
        ears_raw = data.get("ears") or {}
        ears = Table.unserialize([Ear.unserialize(ser) for ser in (ears_raw.values() if isinstance(ears_raw, dict) else ears_raw)])
        return cls(titanic=titanic, splits=splits, ears=ears)


class ConvexComponentOptimizationStepState(State):
    """State for ConvexComponentOptimizationStep. Has convex_components and adjacency. Gallery is read-only."""

    convex_components: Table
    adjacency: Table

    def __init__(
        self,
        convex_components: Table | None = None,
        adjacency: Table | None = None,
    ) -> None:
        self.convex_components = convex_components if convex_components is not None else Table()
        self.adjacency = adjacency if adjacency is not None else Table()

    def serialize(self) -> dict[str, Any]:
        return {
            "convex_components": self.convex_components.serialize(),
            "adjacency": {str(hash(bag.key)): [str(v) for v in bag.items] for bag in self.adjacency},
        }

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "ConvexComponentOptimizationStepState":
        cc_raw = data.get("convex_components") or {}
        cc_list = cc_raw.values() if isinstance(cc_raw, dict) else cc_raw
        convex_components = Table.unserialize([ConvexComponent.unserialize(cc) for cc in cc_list])
        adj_raw = data.get("adjacency") or {}
        adjacency = Table()
        for comp in convex_components.values():
            coll = Collection(comp)
            for id_ser in adj_raw.get(str(hash(comp)), []):
                coll += Identifier(id_ser)
            adjacency.add(coll)
        return cls(convex_components=convex_components, adjacency=adjacency)


class GuardPlacementStepState(State):
    """
    State for GuardPlacementStep. Has component_id_by_point, visibility_by_segment,
    remaining_points, remaining_component_ids, component_id_by_midpoint, and (for suspend/resume)
    guards, visibility, exclusivity. Gallery is read-only; only state is written until completion.
    """

    component_id_by_point: dict[int, list[Identifier]]
    visibility_by_segment: dict[Segment, bool]
    remaining_points: set[Point]
    remaining_component_ids: set[Identifier]
    component_id_by_midpoint: dict[Point, set[Identifier]]
    guards: Table
    visibility: Table
    exclusivity: Table

    def __init__(
        self,
        component_id_by_point: dict[int, list[Identifier]] | None = None,
        visibility_by_segment: dict[Segment, bool] | None = None,
        remaining_points: set[Point] | None = None,
        remaining_component_ids: set[Identifier] | None = None,
        component_id_by_midpoint: dict[Point, set[Identifier]] | None = None,
        guards: Table | None = None,
        visibility: Table | None = None,
        exclusivity: Table | None = None,
    ) -> None:
        self.component_id_by_point = component_id_by_point if component_id_by_point is not None else {}
        self.visibility_by_segment = visibility_by_segment if visibility_by_segment is not None else {}
        self.remaining_points = remaining_points if remaining_points is not None else set()
        self.remaining_component_ids = remaining_component_ids if remaining_component_ids is not None else set()
        self.component_id_by_midpoint = component_id_by_midpoint if component_id_by_midpoint is not None else defaultdict(set)
        self.guards = guards if guards is not None else Table()
        self.visibility = visibility if visibility is not None else Table()
        self.exclusivity = exclusivity if exclusivity is not None else Table()

    def serialize(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "component_id_by_point": {str(k): [str(v) for v in vs] for k, vs in self.component_id_by_point.items()},
            "visibility_by_segment": {str(hash(k)): v for k, v in self.visibility_by_segment.items()},
            "remaining_points": [p.serialize() for p in self.remaining_points],
            "remaining_component_ids": [str(c) for c in self.remaining_component_ids],
            "component_id_by_midpoint": {str(hash(k)): [str(v) for v in vs] for k, vs in self.component_id_by_midpoint.items()},
            "guards": self.guards.serialize(),
            "visibility": {str(hash(bag.key)): [p.serialize() for p in bag.items] for bag in self.visibility},
            "exclusivity": {str(hash(bag.key)): [p.serialize() for p in bag.items] for bag in self.exclusivity},
        }
        return out

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "GuardPlacementStepState":
        component_id_by_point_raw = data.get("component_id_by_point") or {}
        component_id_by_point = {int(k): [Identifier(v) for v in vs] for k, vs in component_id_by_point_raw.items()}

        remaining_points_raw = data.get("remaining_points") or []
        remaining_points = {Point.unserialize(p) for p in remaining_points_raw}

        remaining_component_ids_raw = data.get("remaining_component_ids") or []
        remaining_component_ids = {Identifier(c) for c in remaining_component_ids_raw}

        component_id_by_midpoint: dict[Point, set[Identifier]] = defaultdict(set)

        guards_raw = data.get("guards") or {}
        guards = Table.unserialize([Point.unserialize(v) for v in (guards_raw.values() if isinstance(guards_raw, dict) else [])])
        visibility_raw = data.get("visibility") or {}
        visibility = Table()
        for guard in guards.values():
            coll = Collection(guard)
            for p_ser in visibility_raw.get(str(hash(guard)), []):
                coll += Point.unserialize(p_ser)
            visibility.add(coll)
        exclusivity_raw = data.get("exclusivity") or {}
        exclusivity = Table()
        for guard in guards.values():
            coll = Collection(guard)
            for p_ser in exclusivity_raw.get(str(hash(guard)), []):
                coll += Point.unserialize(p_ser)
            exclusivity.add(coll)

        return cls(
            component_id_by_point=component_id_by_point,
            visibility_by_segment={},
            remaining_points=remaining_points,
            remaining_component_ids=remaining_component_ids,
            component_id_by_midpoint=component_id_by_midpoint,
            guards=guards,
            visibility=visibility,
            exclusivity=exclusivity,
        )
