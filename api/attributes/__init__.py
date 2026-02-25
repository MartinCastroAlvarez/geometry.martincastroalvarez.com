"""
API value types: Timestamp, Countdown, Identifier, Email, Url, Point, Polygon, Segment, Signature, Slug, Interval, Path, Box.
Geometry types (Box, ConvexComponent, Ear, Path, Point, Polygon, Segment, Orientation) are re-exported lazily to avoid circular import.
Data structures (Sequence, Table) live in structs/.
"""

from attributes.countdown import Countdown
from attributes.email import Email
from attributes.identifier import Identifier
from attributes.limit import Limit
from attributes.offset import Offset
from attributes.receipt import ReceiptHandle
from attributes.signature import Signature
from attributes.slug import Slug
from attributes.timestamp import Timestamp
from attributes.url import Url

_GEOMETRY_NAMES = frozenset({
    "Box", "ConvexComponent", "Ear", "Interval", "Orientation", "Path", "Point", "Polygon", "Segment",
})


def __getattr__(name: str):
    if name in _GEOMETRY_NAMES:
        import geometry
        return getattr(geometry, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Box",
    "ConvexComponent",
    "Countdown",
    "Ear",
    "Email",
    "Identifier",
    "Interval",
    "Limit",
    "Offset",
    "Orientation",
    "ReceiptHandle",
    "Path",
    "Point",
    "Polygon",
    "Segment",
    "Signature",
    "Slug",
    "Timestamp",
    "Url",
]
