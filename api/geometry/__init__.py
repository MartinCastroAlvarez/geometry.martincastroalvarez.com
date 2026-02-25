"""
Geometry types: Path, Box, Polygon, Point, Segment, ConvexComponent, Ear, Interval. Orientation re-exported.
"""

from geometry.box import Box
from geometry.convex import ConvexComponent
from geometry.ear import Ear
from geometry.interval import Interval
from geometry.path import Path
from geometry.point import Point
from geometry.polygon import Polygon
from geometry.segment import Segment
from enums.orientation import Orientation

__all__ = [
    "Box",
    "ConvexComponent",
    "Ear",
    "Interval",
    "Orientation",
    "Path",
    "Point",
    "Polygon",
    "Segment",
]
