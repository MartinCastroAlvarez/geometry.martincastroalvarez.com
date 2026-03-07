"""Tests for states package."""

import pytest
from attributes import Identifier
from geometry import Point
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
    """Test StitchingStepState."""

    def test_serialize_empty(self):
        state = StitchingStepState()
        d = state.serialize()
        assert d == {"points": []}

    def test_serialize_with_points(self):
        points = [Point([0, 0]), Point([1, 1])]
        state = StitchingStepState(points=points)
        d = state.serialize()
        assert len(d["points"]) == 2
        assert d["points"][0] == points[0].serialize()
        assert d["points"][1] == points[1].serialize()

    def test_unserialize(self):
        data = {"points": [[0, 0], [1, 1]]}
        state = StitchingStepState.unserialize(data)
        assert len(state.points) == 2
        assert state.points[0] == Point([0, 0])

    def test_unserialize_empty(self):
        state = StitchingStepState.unserialize({})
        assert state.points == []


class TestEarClippingStepState:
    """Test EarClippingStepState."""

    def test_serialize(self):
        state = EarClippingStepState()
        d = state.serialize()
        assert d == {}

    def test_unserialize(self):
        state = EarClippingStepState.unserialize({})
        assert isinstance(state, EarClippingStepState)


class TestConvexComponentOptimizationStepState:
    """Test ConvexComponentOptimizationStepState."""

    def test_serialize(self):
        state = ConvexComponentOptimizationStepState()
        d = state.serialize()
        assert d == {}

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
