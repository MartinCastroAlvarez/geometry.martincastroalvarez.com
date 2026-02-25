"""
Orientation enum for path turn direction (collinear, clockwise, counter-clockwise).
"""

from __future__ import annotations

from enum import Enum


class Orientation(int, Enum):
    COLLINEAR = 0
    CLOCKWISE = -1
    COUNTER_CLOCKWISE = 1
