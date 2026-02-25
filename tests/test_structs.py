"""Tests for structs package."""

from structs import Sequence
from structs import Table


class TestSequence:
    """Test Sequence (ordered list with overlap/merge helpers)."""

    def test_sequence_iter(self):
        s = Sequence([1, 2, 3])
        assert list(s) == [1, 2, 3]

    def test_sequence_len(self):
        s = Sequence([1, 2])
        assert len(s) == 2


class TestTable:
    """Test Table (dict-like by key)."""

    def test_table_empty(self):
        t = Table()
        assert len(t) == 0
