"""Tests for states package."""

import pytest
from attributes import Identifier
from geometry import Point
from geometry import Polygon
from states import ArtGalleryStepState
from states import ConvexComponentOptimizationStepState
from states import EarClippingStepState
from states import GuardPlacementStepState
from states import StitchingStepState
from states import ValidationPolygonStepState

import api  # noqa: F401


class TestArtGalleryStepState:
    """Test ArtGalleryStepState."""

    def test_serialize(self):
        state = ArtGalleryStepState()
        d = state.serialize()
        assert d == {}

    def test_unserialize(self):
        state = ArtGalleryStepState.unserialize({})
        assert isinstance(state, ArtGalleryStepState)


class TestValidationPolygonStepState:
    """Test ValidationPolygonStepState."""

    def test_serialize(self):
        state = ValidationPolygonStepState()
        d = state.serialize()
        assert d == {}

    def test_unserialize(self):
        state = ValidationPolygonStepState.unserialize({})
        assert isinstance(state, ValidationPolygonStepState)


class TestStitchingStepState:
    """Test StitchingStepState (points is Polygon; remaining_obstacles list of Polygon)."""

    def test_serialize_empty(self):
        state = StitchingStepState()
        d = state.serialize()
        assert "points" in d
        assert d["points"] == []
        assert d["stitches"] == []
        assert d["remaining_obstacles"] == []

    def test_serialize_with_points_and_remaining_obstacles(self):
        points = Polygon([Point([0, 0]), Point([1, 0]), Point([1, 1])])
        obstacles = [Polygon([Point([0.25, 0.25]), Point([0.75, 0.25]), Point([0.75, 0.75])])]
        state = StitchingStepState(points=points, remaining_obstacles=obstacles)
        d = state.serialize()
        assert len(d["points"]) == 3
        assert len(d["remaining_obstacles"]) == 1
        assert d["stitches"] == []

    def test_unserialize(self):
        data = {"points": [[0, 0], [1, 0], [1, 1]], "stitches": [], "remaining_obstacles": []}
        state = StitchingStepState.unserialize(data)
        assert len(state.points) == 3
        assert state.points[0] == Point([0, 0])
        assert state.remaining_obstacles == []
        assert state.stitches == []

    def test_unserialize_empty(self):
        state = StitchingStepState.unserialize({})
        assert len(state.points) == 0
        assert state.remaining_obstacles == []
        assert state.stitches == []


class TestEarClippingStepState:
    """Test EarClippingStepState (titanic Polygon, ears Table)."""

    def test_serialize_empty(self):
        state = EarClippingStepState()
        d = state.serialize()
        assert "titanic" in d
        assert "ears" in d
        assert d["titanic"] == []
        assert isinstance(d["ears"], dict)

    def test_unserialize(self):
        state = EarClippingStepState.unserialize({})
        assert isinstance(state, EarClippingStepState)
        assert len(state.titanic) == 0
        assert len(state.ears) == 0


class TestConvexComponentOptimizationStepState:
    """Test ConvexComponentOptimizationStepState (convex_components and adjacency)."""

    def test_serialize(self):
        state = ConvexComponentOptimizationStepState()
        d = state.serialize()
        assert "convex_components" in d
        assert "adjacency" in d
        assert d["convex_components"] == {}
        assert d["adjacency"] == {}

    def test_unserialize(self):
        state = ConvexComponentOptimizationStepState.unserialize({})
        assert isinstance(state, ConvexComponentOptimizationStepState)


class TestGuardPlacementStepState:
    """Test GuardPlacementStepState."""

    def test_serialize_empty(self):
        state = GuardPlacementStepState()
        d = state.serialize()
        assert "component_id_by_point" in d
        assert "visibility_by_segment" in d
        assert "remaining_points" in d
        assert "remaining_component_ids" in d
        assert "component_id_by_midpoint" in d

    def test_serialize_with_data(self):
        state = GuardPlacementStepState(
            component_id_by_point={123: [Identifier("c1")]},
            remaining_points={Point([0, 0])},
            remaining_component_ids={Identifier("c1")},
        )
        d = state.serialize()
        assert "123" in d["component_id_by_point"]
        assert len(d["remaining_points"]) == 1
        assert len(d["remaining_component_ids"]) == 1

    def test_unserialize(self):
        data = {
            "component_id_by_point": {"123": ["c1"]},
            "remaining_points": [[0, 0]],
            "remaining_component_ids": ["c1"],
        }
        state = GuardPlacementStepState.unserialize(data)
        assert 123 in state.component_id_by_point
        assert len(state.remaining_points) == 1
        assert len(state.remaining_component_ids) == 1

    def test_unserialize_empty(self):
        state = GuardPlacementStepState.unserialize({})
        assert state.component_id_by_point == {}
        assert state.remaining_points == set()
        assert state.remaining_component_ids == set()
