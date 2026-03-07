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
from geometry import Point
from geometry import Segment


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
    State for StitchingStep. Has points attribute.
    Access via self.state.points instead of self.points.
    """

    points: list[Point]

    def __init__(self, points: list[Point] | None = None) -> None:
        self.points = points if points is not None else []

    def serialize(self) -> dict[str, Any]:
        return {
            "points": [p.serialize() for p in self.points],
        }

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "StitchingStepState":
        points_raw = data.get("points") or []
        points = [Point.unserialize(p) for p in points_raw]
        return cls(points=points)


class EarClippingStepState(State):
    """State for EarClippingStep. Has no additional attributes."""

    def serialize(self) -> dict[str, Any]:
        return {}

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "EarClippingStepState":
        return cls()


class ConvexComponentOptimizationStepState(State):
    """State for ConvexComponentOptimizationStep. Has no additional attributes."""

    def serialize(self) -> dict[str, Any]:
        return {}

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "ConvexComponentOptimizationStepState":
        return cls()


class GuardPlacementStepState(State):
    """
    State for GuardPlacementStep. Has component_id_by_point, visibility_by_segment,
    remaining_points, remaining_component_ids, component_id_by_midpoint.
    """

    component_id_by_point: dict[int, list[Identifier]]
    visibility_by_segment: dict[Segment, bool]
    remaining_points: set[Point]
    remaining_component_ids: set[Identifier]
    component_id_by_midpoint: dict[Point, set[Identifier]]

    def __init__(
        self,
        component_id_by_point: dict[int, list[Identifier]] | None = None,
        visibility_by_segment: dict[Segment, bool] | None = None,
        remaining_points: set[Point] | None = None,
        remaining_component_ids: set[Identifier] | None = None,
        component_id_by_midpoint: dict[Point, set[Identifier]] | None = None,
    ) -> None:
        self.component_id_by_point = component_id_by_point if component_id_by_point is not None else {}
        self.visibility_by_segment = visibility_by_segment if visibility_by_segment is not None else {}
        self.remaining_points = remaining_points if remaining_points is not None else set()
        self.remaining_component_ids = remaining_component_ids if remaining_component_ids is not None else set()
        self.component_id_by_midpoint = component_id_by_midpoint if component_id_by_midpoint is not None else defaultdict(set)

    def serialize(self) -> dict[str, Any]:
        return {
            "component_id_by_point": {str(k): [str(v) for v in vs] for k, vs in self.component_id_by_point.items()},
            "visibility_by_segment": {str(hash(k)): v for k, v in self.visibility_by_segment.items()},
            "remaining_points": [p.serialize() for p in self.remaining_points],
            "remaining_component_ids": [str(c) for c in self.remaining_component_ids],
            "component_id_by_midpoint": {str(hash(k)): [str(v) for v in vs] for k, vs in self.component_id_by_midpoint.items()},
        }

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> "GuardPlacementStepState":
        component_id_by_point_raw = data.get("component_id_by_point") or {}
        component_id_by_point = {int(k): [Identifier(v) for v in vs] for k, vs in component_id_by_point_raw.items()}

        remaining_points_raw = data.get("remaining_points") or []
        remaining_points = {Point.unserialize(p) for p in remaining_points_raw}

        remaining_component_ids_raw = data.get("remaining_component_ids") or []
        remaining_component_ids = {Identifier(c) for c in remaining_component_ids_raw}

        component_id_by_midpoint: dict[Point, set[Identifier]] = defaultdict(set)

        return cls(
            component_id_by_point=component_id_by_point,
            visibility_by_segment={},
            remaining_points=remaining_points,
            remaining_component_ids=remaining_component_ids,
            component_id_by_midpoint=component_id_by_midpoint,
        )
