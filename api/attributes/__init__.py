"""
API value types and geometry re-exports.

Title
-----
Attributes Package (Value Types and Geometry)

Context
-------
This package defines validated value types used across the API: Timestamp,
Countdown, Identifier, Email, Url, Title, Path, Origin, Limit, Offset,
Slug, Signature, ReceiptHandle. Each enforces format and raises
ValidationError (or a specific exception) on invalid input. Geometry types
(Box, ConvexComponent, Ear, Walk, Point, Polygon, Segment, Interval,
Orientation) are re-exported via __getattr__ from the geometry package to
avoid circular imports. Data structures (Sequence, Table) live in structs/.
Use these types in request/response validation and in domain models.

Examples:
    from attributes import Timestamp, Email, Identifier, Path, Limit
    ts = Timestamp.now()
    email = Email("user@example.com")
    path = Path("/v1/galleries/abc")
    from attributes import Polygon, Point
"""

from attributes.countdown import Countdown
from attributes.email import Email
from attributes.identifier import Identifier
from attributes.limit import Limit
from attributes.offset import Offset
from attributes.origin import Origin
from attributes.path import Path
from attributes.receipt import ReceiptHandle
from attributes.signature import Signature
from attributes.slug import Slug
from attributes.timestamp import Timestamp
from attributes.title import Title
from attributes.url import Url

_GEOMETRY_NAMES = frozenset(
    {
        "Box",
        "ConvexComponent",
        "Ear",
        "Interval",
        "Orientation",
        "Point",
        "Polygon",
        "Segment",
        "Walk",
    }
)


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
    "Origin",
    "Limit",
    "Offset",
    "Orientation",
    "Path",
    "Point",
    "Polygon",
    "ReceiptHandle",
    "Segment",
    "Signature",
    "Slug",
    "Timestamp",
    "Title",
    "Url",
    "Walk",
]
