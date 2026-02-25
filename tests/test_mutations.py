"""Tests for mutations package."""

from mutations.base import Mutation
from mutations.response import MutationResponse


class TestMutationBase:
    """Test Mutation base."""

    def test_mutation_response_typed_dict(self):
        r: MutationResponse = {"ok": True}
        assert r["ok"] is True
