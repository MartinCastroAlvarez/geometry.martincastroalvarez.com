"""
API interfaces: Serializable, Measurable, Spatial, Bounded, Volume.

Title
-----
Interfaces Package

Context
-------
This package defines abstract interfaces used by geometry and models.
Serializable[T] requires serialize() -> T and unserialize(data) -> instance.
Measurable requires a size property (Decimal). Spatial requires contains
and intersects. Bounded requires a box property (Box). Volume requires
signed_area and supports __abs__. Geometry types and models implement
these for consistent persistence and spatial operations. Used for type
hints and to group behavior (e.g. Bounded.intersects via box).

Examples:
>>> isinstance(point, Spatial)
>>> box = segment.box  # Bounded
>>> data = model.serialize()  # Serializable
"""

from interfaces.bounded import Bounded
from interfaces.measurable import Measurable
from interfaces.serializable import Serializable
from interfaces.spatial import Spatial
from interfaces.volume import Volume

__all__ = [
    "Bounded",
    "Measurable",
    "Serializable",
    "Spatial",
    "Volume",
]
