"""
Unit tests for Sequence shift operators (>> and <<).
Shift is the foundation used by StitchingStep to rotate the polygon so vertex is last
and the obstacle so anchor is first before merging. These operators return a new
Sequence; they do not mutate in place.
"""

from structs import Sequence


def test_rshift_puts_element_last_by_index():
    """seq >> index returns a new sequence with the element at that index last."""
    seq = Sequence([10, 20, 30, 40])
    rotated = seq >> 0
    assert list(rotated) == [20, 30, 40, 10]
    assert rotated[-1] == 10
    assert list(seq) == [10, 20, 30, 40], "Original must be unchanged"
    rotated2 = seq >> 2
    assert list(rotated2) == [40, 10, 20, 30]
    assert rotated2[-1] == 30


def test_rshift_puts_element_last_by_value():
    """seq >> element returns a new sequence with that element last (by equality)."""
    seq = Sequence([10, 20, 30, 40])
    rotated = seq >> 30
    assert list(rotated) == [40, 10, 20, 30]
    assert rotated[-1] == 30
    assert list(seq) == [10, 20, 30, 40], "Original must be unchanged"


def test_lshift_puts_element_first_by_index():
    """seq << index returns a new sequence with the element at that index first."""
    seq = Sequence([10, 20, 30, 40])
    rotated = seq << 2
    assert list(rotated) == [30, 40, 10, 20]
    assert rotated[0] == 30
    assert list(seq) == [10, 20, 30, 40], "Original must be unchanged"
    rotated2 = seq << 0
    assert list(rotated2) == [10, 20, 30, 40]


def test_lshift_puts_element_first_by_value():
    """seq << element returns a new sequence with that element first (by equality)."""
    seq = Sequence([10, 20, 30, 40])
    rotated = seq << 30
    assert list(rotated) == [30, 40, 10, 20]
    assert rotated[0] == 30
    assert list(seq) == [10, 20, 30, 40], "Original must be unchanged"


def test_shift_returns_new_sequence_does_not_mutate():
    """Shift operators return a new Sequence; assignment is required to use the result."""
    seq = Sequence([1, 2, 3])
    seq >> 1
    assert list(seq) == [1, 2, 3], "Calling seq >> 1 without assignment must not change seq"
    seq << 2
    assert list(seq) == [1, 2, 3], "Calling seq << 2 without assignment must not change seq"
    # Correct usage: assign the result
    rotated = seq >> 1
    assert rotated[-1] == 2
    seq = seq << 0
    assert seq[0] == 1


def test_shift_usage_for_stitching_left_ends_with_vertex():
    """For stitching: use (left >> index) so vertex is last; assign the result."""
    # Per structs.py: seq >> index puts that index at the end. Use index to get vertex last.
    left = Sequence([100, 200, 300, 400])
    vertex = 300
    idx = left.index(vertex)
    left_rotated = left >> idx
    assert left_rotated is not left
    assert left_rotated[-1] == vertex, "left >> index(vertex) must put vertex last"
    # StitchingStep must assign: left = Polygon(list(stitched >> stitched.index(vertex))) or equivalent.
    assert list(left_rotated) == [400, 100, 200, 300]


def test_shift_usage_for_stitching_right_starts_with_anchor():
    """For stitching: use (right << index) so anchor is first; assign the result."""
    # Per structs.py: seq << index puts that index first. Use index to get anchor first.
    right = Sequence([50, 60, 70])
    anchor = 60
    idx = right.index(anchor)
    right_rotated = right << idx
    assert right_rotated is not right
    assert right_rotated[0] == anchor, "right << index(anchor) must put anchor first"
    assert list(right_rotated) == [60, 70, 50]


def test_shift_empty_sequence():
    """Shift on empty sequence returns empty sequence."""
    seq = Sequence([])
    assert list(seq >> 0) == []
    assert list(seq << 0) == []


def test_shift_single_element():
    """Shift on length-1 sequence returns same single element."""
    seq = Sequence([42])
    assert list(seq >> 0) == [42]
    assert list(seq << 0) == [42]
    assert list(seq >> 42) == [42]


def test_ilshift_in_place_rotates_and_returns_self():
    """seq <<= index mutates seq so that index is first and returns self."""
    seq = Sequence([10, 20, 30, 40])
    ref = seq
    seq <<= 2
    assert ref is seq
    assert list(seq) == [30, 40, 10, 20]
    assert seq[0] == 30


def test_irshift_in_place_rotates_and_returns_self():
    """seq >>= index mutates seq so that index is last and returns self."""
    seq = Sequence([10, 20, 30, 40])
    ref = seq
    seq >>= 1
    assert ref is seq
    assert list(seq) == [30, 40, 10, 20]
    assert seq[-1] == 20
