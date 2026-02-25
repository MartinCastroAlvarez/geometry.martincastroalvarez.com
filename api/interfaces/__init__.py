"""
API interfaces: Serializable, Measurable, Spatial, Bounded, Volume.
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
