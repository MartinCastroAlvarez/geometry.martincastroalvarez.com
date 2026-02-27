"""
Orientation enum for path turn direction (collinear, clockwise, counter-clockwise).

Title
-----
Orientation Enum (Geometric Turn)

Context
-------
Orientation indicates the turn direction of three points: COLLINEAR (0),
CLOCKWISE (-1), COUNTER_CLOCKWISE (1). Used by Walk for signed area and
by Polygon for is_convex and vertex orientation. Integer values allow
numeric comparison. Geometry types (Walk, Polygon) use this to determine
winding order and convexity without string parsing.

Examples:
    walk.orientation  # Orientation.CLOCKWISE
    polygon.is_ccw()  # uses signed_area sign
"""

from __future__ import annotations

from enum import Enum


class Orientation(int, Enum):
    COLLINEAR = 0
    CLOCKWISE = -1
    COUNTER_CLOCKWISE = 1
