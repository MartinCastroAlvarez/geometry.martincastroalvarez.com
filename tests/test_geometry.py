"""Tests for geometry package."""

import json
from decimal import Decimal

import pytest
from exceptions import ValidationError
from geometry import Box
from geometry import ConvexComponent
from geometry import Ear
from geometry import Interval
from geometry import Point
from geometry import Polygon
from geometry import Segment
from geometry import Walk


class TestConvexComponent:
    """Test ConvexComponent (convex polygon, __and__ returns ConvexComponent)."""

    def test_init_empty_or_two_points_allowed(self):
        c = ConvexComponent([])
        assert len(c) == 0
        c2 = ConvexComponent([Point([0, 0]), Point([1, 0])])
        assert len(c2) == 2

    def test_init_convex_triangle_ok(self):
        c = ConvexComponent([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        assert len(c) == 3

    def test_init_non_convex_raises(self):
        with pytest.raises(ValidationError, match="ConvexComponent must be convex"):
            ConvexComponent([Point([0, 0]), Point([1, 0]), Point([1, 1]), Point([0.5, 0.5]), Point([0, 1])])

    def test_and_returns_convex_component(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        q = Polygon([Point([0, 0]), Point([0.5, 1]), Point([1, 0])])
        shared = p & q
        assert isinstance(shared, Polygon)
        c = ConvexComponent([Point([0, 0]), Point([1, 0])])
        d = ConvexComponent([Point([0, 0]), Point([1, 0])])
        result = c & d
        assert isinstance(result, ConvexComponent)
        assert len(result) == 2


class TestPoint:
    """Test Point (2D)."""

    def test_point_serialize(self):
        p = Point([1, 2])
        s = p.serialize()
        assert "1" in s and "2" in s

    def test_point_unserialize_list(self):
        p = Point.unserialize([3, 4])
        assert int(p.x) == 3 and int(p.y) == 4

    def test_init_none_raises(self):
        with pytest.raises(ValidationError, match="Point requires"):
            Point(None)

    def test_init_not_list_or_tuple_raises(self):
        with pytest.raises(ValidationError, match="list or tuple"):
            Point(123)

    def test_init_wrong_length_raises(self):
        with pytest.raises(ValidationError, match="exactly 2"):
            Point([1])
        with pytest.raises(ValidationError, match="exactly 2"):
            Point([1, 2, 3])

    def test_init_invalid_coords_raises(self):
        with pytest.raises(ValidationError, match="valid numbers"):
            Point([None, 0])
        with pytest.raises(ValidationError, match="valid numbers"):
            Point([0, "not a number"])

    def test_init_accepts_tuple_and_decimal(self):
        p = Point((Decimal("1"), Decimal("2")))
        assert p.x == Decimal("1") and p.y == Decimal("2")

    def test_setitem_valid_index_decimal(self):
        p = Point([0, 0])
        p[0] = Decimal("3")
        assert p.x == Decimal("3")
        p[1] = Decimal("4")
        assert p.y == Decimal("4")

    def test_setitem_valid_index_convertible(self):
        p = Point([0, 0])
        p[0] = 5
        p[1] = "6"
        assert p.x == Decimal("5") and p.y == Decimal("6")

    def test_setitem_invalid_index_raises(self):
        p = Point([0, 0])
        with pytest.raises(ValidationError, match="index must be 0 or 1"):
            p[2] = Decimal("0")
        with pytest.raises(ValidationError, match="index must be 0 or 1"):
            p[-1] = Decimal("0")

    def test_setitem_invalid_value_raises(self):
        p = Point([0, 0])
        with pytest.raises(ValidationError, match="Decimal or convertible"):
            p[0] = "not a number"

    def test_x_y_properties(self):
        p = Point([7, 8])
        assert p.x == Decimal("7") and p.y == Decimal("8")

    def test_to_returns_segment(self):
        a = Point([0, 0])
        b = Point([1, 1])
        s = a.to(b)
        assert isinstance(s, Segment)
        assert s[0] == a and s[1] == b

    def test_hash(self):
        p = Point([1, 2])
        h = hash(p)
        assert isinstance(h, int)

    def test_eq_non_point_false(self):
        p = Point([1, 2])
        assert p.__eq__(1) is False
        assert p.__eq__([1, 2]) is False

    def test_eq_same_point_true(self):
        assert Point([1, 2]) == Point([1, 2])

    def test_lt_non_point_not_implemented(self):
        p = Point([1, 2])
        assert p.__lt__(1) is NotImplemented

    def test_lt_different_x(self):
        a = Point([0, 0])
        b = Point([1, 0])
        assert a < b
        assert not (b < a)

    def test_lt_same_x_different_y(self):
        a = Point([0, 0])
        b = Point([0, 1])
        assert a < b
        assert not (b < a)

    def test_sub_non_point_not_implemented(self):
        p = Point([1, 2])
        assert p.__sub__(1) is NotImplemented

    def test_sub_returns_point(self):
        a = Point([5, 10])
        b = Point([2, 3])
        c = a - b
        assert c.x == Decimal("3") and c.y == Decimal("7")

    def test_len_raises(self):
        p = Point([0, 0])
        with pytest.raises(NotImplementedError):
            len(p)

    def test_getitem_index_0_1(self):
        p = Point([1, 2])
        assert p[0] == Decimal("1") and p[1] == Decimal("2")

    def test_getitem_index_out_of_range(self):
        p = Point([0, 0])
        with pytest.raises(IndexError, match="out of range"):
            p[2]
        with pytest.raises(IndexError, match="out of range"):
            p[-1]

    def test_unserialize_empty_str_raises(self):
        with pytest.raises(ValidationError, match="non-empty"):
            Point.unserialize("   ")

    def test_unserialize_invalid_json_raises(self):
        with pytest.raises(ValidationError, match="invalid JSON"):
            Point.unserialize("{]")

    def test_unserialize_json_not_list_raises(self):
        with pytest.raises(ValidationError, match="list of at least 2"):
            Point.unserialize('{"a":1}')

    def test_unserialize_json_list_one_element_raises(self):
        with pytest.raises(ValidationError, match="list of at least 2"):
            Point.unserialize("[1]")

    def test_unserialize_str_json_ok(self):
        p = Point.unserialize("[10, 20]")
        assert p.x == Decimal("10") and p.y == Decimal("20")

    def test_unserialize_non_str_non_list_raises(self):
        with pytest.raises(ValidationError, match="str \\(JSON\\), or list"):
            Point.unserialize(42)


class TestInterval:
    """Test Interval (start, end with start <= end)."""

    def test_init_valid(self):
        i = Interval([Decimal("0"), Decimal("10")])
        assert i.start == Decimal("0") and i.end == Decimal("10")

    def test_init_not_list_raises(self):
        with pytest.raises(ValidationError, match="list of exactly 2"):
            Interval((Decimal("0"), Decimal("10")))

    def test_init_wrong_length_raises(self):
        with pytest.raises(ValidationError, match="list of exactly 2"):
            Interval([Decimal("0")])

    def test_init_not_decimal_raises(self):
        with pytest.raises(ValidationError, match="exactly 2 Decimal"):
            Interval([0, 10])

    def test_init_start_gt_end_raises(self):
        with pytest.raises(ValidationError, match="start must be <= end"):
            Interval([Decimal("10"), Decimal("0")])

    def test_setitem_valid(self):
        i = Interval([Decimal("0"), Decimal("10")])
        i[0] = Decimal("1")
        assert i[0] == Decimal("1")
        i[1] = Decimal("9")
        assert i[1] == Decimal("9")

    def test_setitem_start_gt_end_raises(self):
        i = Interval([Decimal("0"), Decimal("10")])
        with pytest.raises(ValidationError, match="start must be <= end"):
            i[0] = Decimal("20")
        with pytest.raises(ValidationError, match="start must be <= end"):
            i[1] = Decimal("-1")

    def test_setitem_not_decimal_raises(self):
        i = Interval([Decimal("0"), Decimal("10")])
        with pytest.raises(ValidationError, match="must be Decimal"):
            i[0] = 1

    def test_setitem_index_out_of_range(self):
        i = Interval([Decimal("0"), Decimal("10")])
        with pytest.raises(IndexError):
            i[2] = Decimal("0")

    def test_getitem_out_of_range(self):
        i = Interval([Decimal("0"), Decimal("10")])
        with pytest.raises(IndexError):
            i[2]

    def test_size(self):
        i = Interval([Decimal("0"), Decimal("10")])
        assert i.size == Decimal("10")

    def test_contains_decimal_inclusive(self):
        i = Interval([Decimal("0"), Decimal("10")])
        assert i.contains(Decimal("5")) is True
        assert i.contains(Decimal("0")) is True
        assert i.contains(Decimal("10")) is True
        assert i.contains(Decimal("-1")) is False
        assert i.contains(Decimal("11")) is False

    def test_contains_decimal_exclusive(self):
        i = Interval([Decimal("0"), Decimal("10")])
        assert i.contains(Decimal("5"), inclusive=False) is True
        assert i.contains(Decimal("0"), inclusive=False) is False
        assert i.contains(Decimal("10"), inclusive=False) is False

    def test_contains_interval_inclusive(self):
        i = Interval([Decimal("0"), Decimal("10")])
        j = Interval([Decimal("2"), Decimal("8")])
        assert i.contains(j) is True
        assert i.contains(j, inclusive=False) is True
        j2 = Interval([Decimal("0"), Decimal("10")])
        assert i.contains(j2) is True
        assert i.contains(j2, inclusive=False) is False

    def test_contains_invalid_type_raises(self):
        i = Interval([Decimal("0"), Decimal("10")])
        with pytest.raises(ValidationError, match="Decimal or Interval"):
            i.contains(5)

    def test_intersects_inclusive(self):
        i = Interval([Decimal("0"), Decimal("10")])
        j = Interval([Decimal("5"), Decimal("15")])
        assert i.intersects(j) is True
        j2 = Interval([Decimal("10"), Decimal("20")])
        assert i.intersects(j2) is True
        j3 = Interval([Decimal("11"), Decimal("20")])
        assert i.intersects(j3) is False

    def test_intersects_exclusive(self):
        i = Interval([Decimal("0"), Decimal("10")])
        j = Interval([Decimal("10"), Decimal("20")])
        assert i.intersects(j, inclusive=False) is False

    def test_intersects_not_interval_raises(self):
        i = Interval([Decimal("0"), Decimal("10")])
        with pytest.raises(ValidationError, match="expects Interval"):
            i.intersects(5)

    def test_serialize(self):
        i = Interval([Decimal("0"), Decimal("10")])
        assert i.serialize() == ["0", "10"]

    def test_unserialize_valid(self):
        i = Interval.unserialize([0, 10])
        assert i[0] == Decimal("0") and i[1] == Decimal("10")
        i2 = Interval.unserialize([Decimal("1"), Decimal("2")])
        assert i2.start == Decimal("1") and i2.end == Decimal("2")

    def test_unserialize_invalid_raises(self):
        with pytest.raises(ValidationError, match="list of at least 2"):
            Interval.unserialize([])
        with pytest.raises(ValidationError, match="list of at least 2"):
            Interval.unserialize(1)
        with pytest.raises(ValidationError, match="valid numbers"):
            Interval.unserialize(["x", "y"])


class TestBox:
    """Test Box (axis-aligned)."""

    def _rect(self, min_x=0, min_y=0, max_x=1, max_y=1):
        return Box(
            bottom_left=Point((min_x, min_y)),
            top_left=Point((min_x, max_y)),
            bottom_right=Point((max_x, min_y)),
            top_right=Point((max_x, max_y)),
        )

    def test_init_from_points(self):
        b = self._rect()
        assert b.bottom_left.x == Decimal("0") and b.bottom_left.y == Decimal("0")
        assert b.top_right.x == Decimal("1") and b.top_right.y == Decimal("1")

    def test_init_from_lists_converted_to_point(self):
        b = Box(
            bottom_left=[0, 0],
            top_left=[0, 1],
            bottom_right=[1, 0],
            top_right=[1, 1],
        )
        assert b[0].x == Decimal("0")

    def test_init_invalid_left_edge_raises(self):
        from exceptions import BoxInvalidEdgeError

        with pytest.raises(BoxInvalidEdgeError, match="vertical left"):
            Box(
                bottom_left=Point([0, 0]),
                top_left=Point([1, 1]),
                bottom_right=Point([1, 0]),
                top_right=Point([1, 1]),
            )

    def test_init_invalid_bottom_edge_raises(self):
        from exceptions import BoxInvalidEdgeError

        with pytest.raises(BoxInvalidEdgeError, match="horizontal bottom"):
            Box(
                bottom_left=Point([0, 0]),
                top_left=Point([0, 1]),
                bottom_right=Point([1, 1]),
                top_right=Point([1, 1]),
            )

    def test_serialize_unserialize(self):
        b = self._rect(1, 2, 3, 4)
        d = b.serialize()
        assert "bottom_left" in d and "top_right" in d
        b2 = Box.unserialize(d)
        assert b2.bottom_left.x == b.bottom_left.x and b2.top_right.y == b.top_right.y

    def test_unserialize_not_dict_raises(self):
        from exceptions import SerializedInvalidDictError

        with pytest.raises(SerializedInvalidDictError, match="expects a dict"):
            Box.unserialize([])

    def test_unserialize_missing_key_raises(self):
        from exceptions import BoxInvalidEdgeError

        with pytest.raises(BoxInvalidEdgeError, match="missing key"):
            Box.unserialize({"bottom_left": [0, 0]})

    def test_x_y_properties(self):
        b = self._rect(0, 0, 2, 3)
        assert b.x.start == Decimal("0") and b.x.end == Decimal("2")
        assert b.y.start == Decimal("0") and b.y.end == Decimal("3")

    def test_getitem(self):
        b = self._rect()
        assert b[0] is b.bottom_left and b[1] is b.top_left
        assert b[2] is b.bottom_right and b[3] is b.top_right
        with pytest.raises(IndexError):
            b[4]

    def test_intersects_box(self):
        a = self._rect(0, 0, 2, 2)
        b = self._rect(1, 1, 3, 3)
        assert a.intersects(b) is True
        c = self._rect(3, 3, 4, 4)
        assert a.intersects(c) is False

    def test_intersects_bounded(self):
        seg = Segment([Point([0, 0]), Point([1, 1])])
        box = self._rect(0, 0, 2, 2)
        assert box.intersects(seg) is True
        box2 = self._rect(5, 5, 6, 6)
        assert box2.intersects(seg) is False

    def test_intersects_other_raises(self):
        b = self._rect()
        with pytest.raises(NotImplementedError, match="not implemented"):
            b.intersects(1)

    def test_contains_point(self):
        b = self._rect(0, 0, 2, 2)
        assert b.contains(Point([1, 1])) is True
        assert b.contains(Point([0, 0])) is True
        assert b.contains(Point([-1, 0])) is False

    def test_contains_box(self):
        a = self._rect(0, 0, 4, 4)
        b = self._rect(1, 1, 2, 2)
        assert a.contains(b) is True
        assert b.contains(a) is False

    def test_contains_bounded(self):
        seg = Segment([Point([0.5, 0.5]), Point([1, 1])])
        b = self._rect(0, 0, 2, 2)
        assert b.contains(seg) is True

    def test_contains_other_raises(self):
        b = self._rect()
        with pytest.raises(NotImplementedError, match="not implemented"):
            b.contains(1)


class TestWalk:
    """Test Walk (start, center, end) orientation."""

    def test_init_from_points(self):
        a = Point([0, 0])
        b = Point([1, 0])
        c = Point([0, 1])
        w = Walk(start=a, center=b, end=c)
        assert w[0] is a and w[1] is b and w[2] is c

    def test_init_from_lists(self):
        w = Walk(start=[0, 0], center=[1, 0], end=[0, 1])
        assert w[0].x == Decimal("0") and w[1].x == Decimal("1")

    def test_signed_area_collinear_zero(self):
        w = Walk(start=[0, 0], center=[1, 0], end=[2, 0])
        assert w.signed_area == Decimal("0")
        w2 = Walk(start=[0, 0], center=[0, 0], end=[1, 1])
        assert w2.signed_area == Decimal("0")

    def test_signed_area_ccw_positive(self):
        w = Walk(start=[0, 0], center=[1, 0], end=[0, 1])
        assert w.signed_area > 0

    def test_signed_area_cw_negative(self):
        w = Walk(start=[0, 0], center=[0, 1], end=[1, 0])
        assert w.signed_area < 0

    def test_orientation_ccw_cw_collinear(self):
        w_ccw = Walk(start=[0, 0], center=[1, 0], end=[0, 1])
        assert w_ccw.orientation.name == "COUNTER_CLOCKWISE"
        assert w_ccw.is_ccw() is True and w_ccw.is_cw() is False and w_ccw.is_collinear() is False
        w_cw = Walk(start=[0, 0], center=[0, 1], end=[1, 0])
        assert w_cw.is_cw() is True and w_cw.is_ccw() is False
        w_col = Walk(start=[0, 0], center=[1, 0], end=[2, 0])
        assert w_col.is_collinear() is True

    def test_getitem_out_of_range(self):
        w = Walk(start=[0, 0], center=[1, 0], end=[0, 1])
        with pytest.raises(IndexError):
            w[3]


class TestEar:
    """Test Ear (triangle, ccw or cw)."""

    def test_init_three_points_ccw_ok(self):
        e = Ear([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        assert len(e) == 3

    def test_init_three_points_cw_ok(self):
        e = Ear([Point([0, 0]), Point([0.5, 1]), Point([1, 0])])
        assert len(e) == 3

    def test_init_not_three_raises(self):
        with pytest.raises(ValidationError, match="exactly 3 points"):
            Ear([Point([0, 0]), Point([1, 0])])
        with pytest.raises(ValidationError, match="exactly 3 points"):
            Ear([Point([0, 0]), Point([1, 0]), Point([0.5, 1]), Point([0, 1])])

    def test_init_collinear_raises(self):
        with pytest.raises(ValidationError, match="ConvexComponent must be convex"):
            Ear([Point([0, 0]), Point([1, 0]), Point([2, 0])])

    def test_and_ear_returns_convex_component(self):
        e1 = Ear([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        e2 = Ear([Point([0, 0]), Point([0.5, 1]), Point([1, 0])])
        result = e1 & e2
        assert isinstance(result, ConvexComponent)

    def test_and_non_ear_returns_not_implemented(self):
        e = Ear([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        assert e.__and__(Point([0, 0])) is NotImplemented

    def test_and_with_polygon_returns_convex_component(self):
        e = Ear([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        p = Polygon([Point([0, 0]), Point([0.5, 1]), Point([1, 0])])
        result = e & p
        assert isinstance(result, ConvexComponent)


class TestSegment:
    """Test Segment (two Points)."""

    def test_init_valid(self):
        s = Segment([Point([0, 0]), Point([1, 1])])
        assert s.start == Point([0, 0]) and s.end == Point([1, 1])

    def test_init_none_raises(self):
        with pytest.raises(ValidationError, match="got None"):
            Segment(None)

    def test_init_not_list_raises(self):
        with pytest.raises(ValidationError, match="must be a list"):
            Segment((Point([0, 0]), Point([1, 1])))

    def test_init_empty_raises(self):
        with pytest.raises(ValidationError, match="empty list"):
            Segment([])

    def test_init_wrong_length_raises(self):
        with pytest.raises(ValidationError, match="exactly 2"):
            Segment([Point([0, 0])])
        with pytest.raises(ValidationError, match="exactly 2"):
            Segment([Point([0, 0]), Point([1, 0]), Point([2, 0])])

    def test_init_not_point_raises(self):
        with pytest.raises(ValidationError, match="start must be a Point"):
            Segment([[0, 0], Point([1, 1])])
        with pytest.raises(ValidationError, match="end must be a Point"):
            Segment([Point([0, 0]), [1, 1]])

    def test_getitem(self):
        s = Segment([Point([0, 0]), Point([1, 1])])
        assert s[0] == Point([0, 0]) and s[1] == Point([1, 1])
        with pytest.raises(IndexError):
            s[2]

    def test_hash_eq(self):
        s1 = Segment([Point([0, 0]), Point([1, 1])])
        s2 = Segment([Point([1, 1]), Point([0, 0])])
        assert hash(s1) == hash(s2)
        assert s1 == s2
        assert s1 != Point([0, 0])

    def test_invert(self):
        s = Segment([Point([0, 0]), Point([1, 1])])
        t = ~s
        assert t[0] == Point([1, 1]) and t[1] == Point([0, 0])

    def test_size_midpoint_box(self):
        s = Segment([Point([0, 0]), Point([2, 0])])
        assert s.size == Decimal("2")
        assert s.midpoint.x == Decimal("1") and s.midpoint.y == Decimal("0")
        b = s.box
        assert b.bottom_left.x == Decimal("0") and b.top_right.x == Decimal("2")

    def test_contains_point_on_segment(self):
        s = Segment([Point([0, 0]), Point([2, 0])])
        assert s.contains(Point([1, 0])) is True
        assert s.contains(Point([0, 0])) is True

    def test_contains_point_off_segment(self):
        s = Segment([Point([0, 0]), Point([2, 0])])
        assert s.contains(Point([1, 1])) is False

    def test_contains_segment(self):
        s = Segment([Point([0, 0]), Point([2, 0])])
        t = Segment([Point([0.5, 0]), Point([1, 0])])
        assert s.contains(t) is True

    def test_contains_other_raises(self):
        s = Segment([Point([0, 0]), Point([1, 0])])
        with pytest.raises(NotImplementedError, match="Point or Segment"):
            s.contains(1)

    def test_intersects_crossing(self):
        s1 = Segment([Point([0, 0]), Point([2, 2])])
        s2 = Segment([Point([0, 2]), Point([2, 0])])
        assert s1.intersects(s2) is True

    def test_intersects_disjoint(self):
        s1 = Segment([Point([0, 0]), Point([1, 0])])
        s2 = Segment([Point([2, 0]), Point([3, 0])])
        assert s1.intersects(s2) is False

    def test_intersects_collinear_overlap(self):
        s1 = Segment([Point([0, 0]), Point([2, 0])])
        s2 = Segment([Point([1, 0]), Point([3, 0])])
        assert s1.intersects(s2) is True

    def test_intersects_non_segment_raises(self):
        s = Segment([Point([0, 0]), Point([1, 0])])
        with pytest.raises(NotImplementedError, match="only supports Segment"):
            s.intersects(Point([0, 0]))

    def test_connects(self):
        a = Point([0, 0])
        b = Point([1, 0])
        c = Point([2, 0])
        s1 = Segment([a, b])
        s2 = Segment([b, c])
        assert s1.connects(s2) is True
        s3 = Segment([a, c])
        assert s1.connects(s3) is True
        s4 = Segment([Point([3, 0]), Point([4, 0])])
        assert s1.connects(s4) is False

    def test_serialize_unserialize(self):
        s = Segment([Point([0, 0]), Point([1, 1])])
        data = s.serialize()
        assert len(data) == 2
        t = Segment.unserialize(data)
        assert t[0] == s[0] and t[1] == s[1]

    def test_unserialize_invalid_raises(self):
        with pytest.raises(ValidationError, match="exactly 2 Point"):
            Segment.unserialize([])
        with pytest.raises(ValidationError, match="exactly 2 Point"):
            Segment.unserialize([Point([0, 0]).serialize()])


class TestPolygon:
    """Test Polygon (closed chain of Points)."""

    def test_init_empty_or_none(self):
        p = Polygon()
        assert len(p) == 0
        p2 = Polygon(None)
        assert len(p) == 0

    def test_init_non_list_iterable(self):
        p = Polygon((Point([0, 0]), Point([1, 0]), Point([0, 1])))
        assert len(p) == 3

    def test_init_non_point_raises(self):
        with pytest.raises(ValidationError, match="must be a Point"):
            Polygon([Point([0, 0]), [1, 0]])

    def test_edges_empty(self):
        p = Polygon([])
        assert list(p.edges) == []

    def test_degree_vertex_in_polygon(self):
        """Each vertex in a simple polygon has degree 2 (appears once)."""
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        assert p.degree(Point([0, 0])) == 2
        assert p.degree(Point([1, 0])) == 2
        assert p.degree(Point([0.5, 1])) == 2

    def test_degree_point_not_vertex_returns_zero(self):
        """Point not in polygon has degree 0."""
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        assert p.degree(Point([2, 2])) == 0

    def test_degree_single_point_polygon(self):
        """Single-vertex polygon: that point has degree 2."""
        p = Polygon([Point([0, 0])])
        assert p.degree(Point([0, 0])) == 2

    def test_box_empty_raises(self):
        with pytest.raises(ValidationError, match="at least one point"):
            Polygon().box

    def test_box_triangle(self):
        p = Polygon([Point([0, 0]), Point([2, 0]), Point([1, 2])])
        b = p.box
        assert b.bottom_left.x == Decimal("0") and b.bottom_left.y == Decimal("0")
        assert b.top_right.x == Decimal("2") and b.top_right.y == Decimal("2")

    def test_contains_other_raises(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0, 1])])
        with pytest.raises(NotImplementedError, match="Point, Segment, Polygon"):
            p.contains(1)

    def test_intersects_other_raises(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0, 1])])
        with pytest.raises(NotImplementedError, match="Point, Segment, Box, Polygon"):
            p.intersects(1)

    def test_serialize_unserialize(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0, 1])])
        data = p.serialize()
        assert len(data) == 3
        q = Polygon.unserialize(data)
        assert len(q) == 3 and q[0] == p[0]

    def test_unserialize_not_list_raises(self):
        with pytest.raises(ValidationError, match="expects a list"):
            Polygon.unserialize("not a list")

    def test_and_shared_edge(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        q = Polygon([Point([0, 0]), Point([0.5, 1]), Point([1, 0])])
        shared = p & q
        assert len(shared) == 2
        pts = set(shared)
        assert Point([0, 0]) in pts and (Point([1, 0]) in pts or Point([0.5, 1]) in pts)

    def test_and_not_polygon_returns_not_implemented(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0, 1])])
        assert p.__and__(1) is NotImplemented

    def test_and_no_shared_edge_raises(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0, 1])])
        q = Polygon([Point([2, 0]), Point([3, 0]), Point([2.5, 1])])
        with pytest.raises(ValidationError, match="do not share an edge"):
            p & q

    def test_and_too_few_vertices_raises(self):
        p = Polygon([Point([0, 0])])
        q = Polygon([Point([0, 0]), Point([1, 0])])
        with pytest.raises(ValidationError, match="do not share an edge"):
            p & q

    def test_signed_area(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0, 1])])
        assert p.signed_area == Decimal("0.5")
        empty = Polygon([])
        assert empty.signed_area == Decimal("0")
        two = Polygon([Point([0, 0]), Point([1, 0])])
        assert two.signed_area == Decimal("0")

    def test_is_ccw_is_cw(self):
        ccw = Polygon([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        assert ccw.is_ccw() is True and ccw.is_cw() is False
        cw = Polygon([Point([0, 0]), Point([0.5, 1]), Point([1, 0])])
        assert cw.is_cw() is True and cw.is_ccw() is False
        assert Polygon([]).is_ccw() is False
        assert Polygon([Point([0, 0]), Point([1, 0])]).is_ccw() is False

    def test_is_convex(self):
        tri = Polygon([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        assert tri.is_convex() is True
        square = Polygon([Point([0, 0]), Point([1, 0]), Point([1, 1]), Point([0, 1])])
        assert square.is_convex() is True
        concave = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([1, 1]), Point([0, 2])])
        assert concave.is_convex() is False
        assert Polygon([]).is_convex() is False
        assert Polygon([Point([0, 0]), Point([1, 0])]).is_convex() is False

    def test_edges_triangle(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([0.5, 1])])
        edges = list(p.edges)
        assert len(edges) == 3
        assert all(isinstance(e, Segment) for e in edges)

    def test_contains_point_outside_box(self):
        square = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([0, 2])])
        assert square.contains(Point([5, 5])) is False

    def test_contains_point_on_edge_inclusive(self):
        square = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([0, 2])])
        assert square.contains(Point([1, 0]), inclusive=True) is True

    def test_contains_point_inside_ray_casting(self):
        square = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([0, 2])])
        assert square.contains(Point([1, 1])) is True
        assert square.contains(Point([0.5, 0.5])) is True

    def test_contains_point_inclusive_false_not_on_edge(self):
        square = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([0, 2])])
        assert square.contains(Point([1, 1]), inclusive=False) is True

    def test_contains_segment_outside_box(self):
        square = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([0, 2])])
        seg = Segment([Point([5, 5]), Point([6, 6])])
        assert square.contains(seg) is False

    def test_contains_segment_equals_edge(self):
        square = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([0, 2])])
        seg = Segment([Point([0, 0]), Point([2, 0])])
        assert square.contains(seg, inclusive=True) is True

    def test_contains_segment_fully_inside(self):
        square = Polygon([Point([0, 0]), Point([4, 0]), Point([4, 4]), Point([0, 4])])
        seg = Segment([Point([1, 1]), Point([2, 2])])
        assert square.contains(seg) is True

    def test_contains_polygon(self):
        outer = Polygon([Point([0, 0]), Point([4, 0]), Point([4, 4]), Point([0, 4])])
        inner = Polygon([Point([1, 1]), Point([2, 1]), Point([2, 2]), Point([1, 2])])
        assert outer.contains(inner) is True
        assert inner.contains(outer) is False

    def test_intersects_point(self):
        square = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([0, 2])])
        assert square.intersects(Point([1, 1])) is True
        assert square.intersects(Point([5, 5])) is False

    def test_intersects_segment_vertex_on_edge(self):
        square = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([0, 2])])
        seg = Segment([Point([1, 0]), Point([1, 1])])
        assert square.intersects(seg, inclusive=True) is True

    def test_intersects_segment_crossing(self):
        square = Polygon([Point([0, 0]), Point([2, 0]), Point([2, 2]), Point([0, 2])])
        seg = Segment([Point([-1, 1]), Point([3, 1])])
        assert square.intersects(seg) is True

    def test_intersects_box_no_overlap(self):
        p = Polygon([Point([0, 0]), Point([1, 0]), Point([1, 1]), Point([0, 1])])
        box = Box(
            bottom_left=Point([5, 5]),
            top_left=Point([5, 6]),
            bottom_right=Point([6, 5]),
            top_right=Point([6, 6]),
        )
        assert p.intersects(box) is False

    def test_intersects_box_corner_inside(self):
        square = Polygon([Point([0, 0]), Point([4, 0]), Point([4, 4]), Point([0, 4])])
        box = Box(
            bottom_left=Point([2, 2]),
            top_left=Point([2, 5]),
            bottom_right=Point([5, 2]),
            top_right=Point([5, 5]),
        )
        assert square.intersects(box) is True

    def test_intersects_polygon_no_box_overlap(self):
        p1 = Polygon([Point([0, 0]), Point([1, 0]), Point([1, 1]), Point([0, 1])])
        p2 = Polygon([Point([5, 5]), Point([6, 5]), Point([6, 6]), Point([5, 6])])
        assert p1.intersects(p2) is False

    def test_intersects_polygon_vertex_inside(self):
        p1 = Polygon([Point([0, 0]), Point([4, 0]), Point([4, 4]), Point([0, 4])])
        p2 = Polygon([Point([2, 2]), Point([6, 2]), Point([6, 6]), Point([2, 6])])
        assert p1.intersects(p2) is True

    def test_is_simple_true(self):
        square = Polygon([Point([0, 0]), Point([1, 0]), Point([1, 1]), Point([0, 1])])
        assert square.is_simple() is True

    def test_is_simple_false_self_intersecting(self):
        bowtie = Polygon([Point([0, 0]), Point([2, 2]), Point([2, 0]), Point([0, 2])])
        assert bowtie.is_simple() is False

    def test_is_simple_less_than_three_vertices(self):
        assert Polygon([]).is_simple() is False
        assert Polygon([Point([0, 0]), Point([1, 0])]).is_simple() is False
