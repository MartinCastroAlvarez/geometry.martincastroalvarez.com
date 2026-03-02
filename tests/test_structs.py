"""Tests for structs package."""

import pytest
from exceptions import SequenceMultipleOverlapsError
from exceptions import ValidationError
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

    def test_sequence_init_none(self):
        assert list(Sequence(None)) == []

    def test_sequence_getitem_int_wraps(self):
        s = Sequence([10, 20, 30])
        assert s[0] == 10 and s[3] == 10 and s[-1] == 30

    def test_sequence_getitem_slice_no_wrap(self):
        s = Sequence([1, 2, 3, 4])
        assert list(s[1:3]) == [2, 3]

    def test_sequence_getitem_slice_wrap(self):
        s = Sequence([1, 2, 3])
        # 2:4 with wrap: s=2, e=1 -> [self[2], self[0]] = [3, 1]
        assert list(s[2:4]) == [3, 1]

    def test_sequence_getitem_slice_step_raises(self):
        s = Sequence([1, 2, 3])
        with pytest.raises(ValueError, match="step"):
            _ = s[::2]

    def test_sequence_getitem_empty_raises(self):
        s = Sequence([])
        with pytest.raises(IndexError):
            _ = s[0]

    def test_sequence_lshift_int(self):
        s = Sequence([1, 2, 3])
        r = s << 1
        assert list(r) == [2, 3, 1]

    def test_sequence_lshift_element(self):
        s = Sequence([10.0, 20.0, 30.0])
        r = s << 20.0  # rotate so element 20.0 is first (not int index)
        assert list(r) == [20.0, 30.0, 10.0]

    def test_sequence_rshift_int(self):
        s = Sequence([1, 2, 3])
        r = s >> 0
        assert list(r) == [2, 3, 1]

    def test_sequence_add(self):
        a = Sequence([1, 2])
        b = Sequence([3, 4])
        assert list(a + b) == [1, 2, 3, 4]

    def test_sequence_add_non_sequence_returns_not_implemented(self):
        a = Sequence([1, 2])
        assert a.__add__([3, 4]) is NotImplemented

    def test_sequence_iadd(self):
        a = Sequence([1, 2])
        a += Sequence([3])
        assert list(a) == [1, 2, 3]

    def test_sequence_sub_contiguous(self):
        s = Sequence([1, 2, 3, 4])
        r = s - Sequence([2, 3])
        assert list(r) == [4, 1]

    def test_sequence_sub_whole_returns_empty(self):
        s = Sequence([1, 2])
        r = s - Sequence([1, 2])
        assert list(r) == []

    def test_sequence_sub_no_match_returns_copy(self):
        s = Sequence([1, 2, 3])
        r = s - Sequence([5, 6])
        assert list(r) == [1, 2, 3]

    def test_sequence_isub(self):
        s = Sequence([1, 2, 3, 4])
        s -= Sequence([2, 3])
        assert list(s) == [4, 1]

    def test_sequence_and_single_overlap(self):
        a = Sequence([1])
        b = Sequence([1])
        r = a & b
        assert list(r) == [1]

    def test_sequence_and_empty(self):
        a = Sequence([1, 2])
        b = Sequence([3, 4])
        r = a & b
        assert list(r) == []

    def test_sequence_and_multiple_overlaps_raises(self):
        a = Sequence([1, 2, 1, 2])
        b = Sequence([1, 2])
        with pytest.raises(SequenceMultipleOverlapsError, match="multiple"):
            _ = a & b

    def test_sequence_invert(self):
        s = Sequence([1, 2, 3])
        r = ~s
        assert list(r) == [3, 2, 1]

    def test_sequence_hash_empty(self):
        s = Sequence([])
        assert hash(s) is not None

    def test_sequence_contains_element(self):
        s = Sequence([1, 2, 3])
        assert 2 in s
        assert 5 not in s

    def test_sequence_contains_subsequence(self):
        s = Sequence([1, 2, 3, 4])
        assert Sequence([2, 3]) in s
        assert Sequence([4, 1]) in s  # wrap
        assert Sequence([1, 3]) not in s

    def test_sequence_index(self):
        s = Sequence([10, 20, 30])
        assert s.index(20) == 1

    def test_sequence_append(self):
        s = Sequence([1, 2])
        s.append(3)
        assert list(s) == [1, 2, 3]

    def test_sequence_insert(self):
        s = Sequence([1, 3])
        s.insert(1, 2)
        assert list(s) == [1, 2, 3]

    def test_sequence_pop_index(self):
        s = Sequence([1, 2, 3])
        assert s.pop(1) == 2
        assert list(s) == [1, 3]

    def test_sequence_pop_element(self):
        s = Sequence(["a", "b", "c"])
        assert s.pop("b") == "b"
        assert list(s) == ["a", "c"]

    def test_sequence_dedup(self):
        s = Sequence([1, 1, 2, 2, 3])
        r = s.dedup()
        assert list(r) == [1, 2, 3]

    def test_sequence_serialize(self):
        s = Sequence([1, 2, 3])
        assert s.serialize() == [1, 2, 3]

    def test_sequence_unserialize(self):
        s = Sequence.unserialize([1, 2, 3])
        assert list(s) == [1, 2, 3]

    def test_sequence_unserialize_not_list(self):
        s = Sequence.unserialize(None)
        assert list(s) == []


class TestTable:
    """Test Table (dict-like by key)."""

    def test_table_empty(self):
        t = Table()
        assert len(t) == 0

    def test_table_add(self):
        t = Table()
        t.add(1)
        t.add(2)
        assert len(t) == 2
        assert 1 in t and 2 in t

    def test_table_iadd(self):
        t = Table()
        t += 10
        assert 10 in t

    def test_table_isub_by_key(self):
        t = Table()
        t.add("a")
        t.add("b")
        key = hash("a")
        t -= key
        assert "a" not in t

    def test_table_isub_by_item(self):
        t = Table()
        t.add("x")
        t -= "x"
        assert "x" not in t

    def test_table_contains_by_key(self):
        t = Table()
        t.add(42)
        assert hash(42) in t

    def test_table_contains_by_item(self):
        t = Table()
        t.add("foo")
        assert "foo" in t

    def test_table_getitem_by_key_or_item(self):
        t = Table()
        t.add("foo")
        t.add("bar")
        assert t[hash("foo")] == "foo"
        assert t["foo"] == "foo"
        assert t["bar"] == "bar"
        with pytest.raises(KeyError):
            _ = t["baz"]

    def test_table_iter(self):
        t = Table()
        t.add(1)
        t.add(2)
        assert set(t) == {1, 2}

    def test_table_hash(self):
        t = Table()
        t.add(1)
        t.add(2)
        assert hash(t) is not None

    def test_table_or_merge(self):
        a = Table()
        a.add(1)
        b = Table()
        b.add(2)
        r = a | b
        assert len(r) == 2
        assert 1 in r and 2 in r

    def test_table_or_non_table_returns_not_implemented(self):
        t = Table()
        t.add(1)
        assert t.__or__({}) is NotImplemented

    def test_table_serialize(self):
        class SerializableItem:
            def __init__(self, val):
                self.val = val

            def serialize(self):
                return {"v": self.val}

        t = Table()
        t.add(SerializableItem(1))
        t.add(SerializableItem(2))
        d = t.serialize()
        assert isinstance(d, dict)
        assert len(d) == 2
        assert all("v" in v for v in d.values())

    def test_table_unserialize_list(self):
        t = Table.unserialize([1, 2, 3])
        assert len(t) == 3

    def test_table_unserialize_dict_key_mismatch_raises(self):
        with pytest.raises(ValidationError, match="key does not match"):
            Table.unserialize({str(hash(1)): 2})
