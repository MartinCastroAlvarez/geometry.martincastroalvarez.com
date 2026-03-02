"""
Visibility: guard (Point) plus ordered list of points (visibility polygon). Hash = hash(guard).

Title
-----
Visibility (Guard and Visible Region)

Context
-------
Visibility pairs a guard point with the ordered list of points forming its visible region
boundary. Used for art gallery guard placement; serialized as dict sharing keys with the
guards table, value = list of serialized points. __hash__ is the guard's hash so that
Table[Visibility] keys match Table[Point] keys for guards.

Examples:
>>> vis = Visibility(guard, [p1, p2, p3])
>>> vis.serialize()  # list of [x,y]
"""

from __future__ import annotations

from typing import Any

from exceptions import ValidationError
from geometry.point import Point
from interfaces import Serializable


class Visibility(Serializable[list[list[str]]]):
    """
    A guard and its visibility polygon (ordered list of points). Hash equals hash(guard).
    """

    def __init__(self, guard: Point, points: list[Point] | None = None) -> None:
        if guard is None:
            raise ValidationError("Visibility requires a guard (Point)")
        self._guard: Point = guard
        self._points: list[Point] = list(points) if points else []

    @property
    def guard(self) -> Point:
        return self._guard

    @property
    def points(self) -> list[Point]:
        return self._points

    def __hash__(self) -> int:
        return hash(self._guard)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Visibility):
            return False
        return self._guard == other._guard and self._points == other._points

    def serialize(self) -> list[list[str]]:
        """Return list of serialized points [[x,y], ...] for wire format."""
        return [p.serialize() for p in self._points]

    @classmethod
    def unserialize(cls, data: Any) -> Visibility:
        """Build Visibility from dict with 'guard' and 'points' keys, or from list of point coords (guard must be supplied elsewhere)."""
        if isinstance(data, dict):
            guard_data = data.get("guard")
            points_data = data.get("points")
            if guard_data is None:
                raise ValidationError("Visibility.unserialize dict must have 'guard'")
            if points_data is None or not isinstance(points_data, (list, tuple)):
                raise ValidationError("Visibility.unserialize dict must have 'points' as list")
            guard = Point.unserialize(guard_data)
            points = [Point.unserialize(p) for p in points_data]
            return cls(guard, points)
        if isinstance(data, (list, tuple)):
            points = [Point.unserialize(p) for p in data]
            if not points:
                raise ValidationError("Visibility.unserialize list must have at least one point")
            raise ValidationError("Visibility.unserialize(list) cannot infer guard; use dict with 'guard' and 'points' or Visibility(guard, points)")
        raise ValidationError("Visibility.unserialize expects dict or list")
