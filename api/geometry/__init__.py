"""
Geometry types for art gallery polygons and spatial operations.

Title
-----
Geometry Package

Context
-------
This package provides 2D geometry types used for gallery boundaries,
obstacles, ears, convex components, and guards. Point is (x,y) as Decimal;
Segment is two Points; Polygon is a closed sequence of Points; Box is
axis-aligned; Interval is [start, end]; Walk is three Points for turn
orientation. ConvexComponent and Ear are specialized polygons. Types
implement Spatial (contains, intersects), Bounded (box), Measurable (size),
Volume (signed_area), and Serializable for JSON/S3. Orientation is the
enum for collinear/clockwise/counter-clockwise. Used by models.ArtGallery
and by the pipeline (ear clipping, visibility, guard placement).

Examples:
>>> from geometry import Point, Polygon, Segment, Box
>>> p = Point.unserialize([1, 2])
>>> poly = Polygon.unserialize([[0,0], [1,0], [1,1], [0,1]])
"""

from enums.orientation import Orientation
from geometry.box import Box
from geometry.convex import ConvexComponent
from geometry.ear import Ear
from geometry.interval import Interval
from geometry.point import Point
from geometry.polygon import Polygon
from geometry.segment import Segment
from geometry.walk import Walk

__all__ = [
    "Box",
    "ConvexComponent",
    "Ear",
    "Interval",
    "Orientation",
    "Point",
    "Polygon",
    "Segment",
    "Walk",
]
