"""
Data structures: Sequence[T], Table[T].

Title
-----
Structs Package

Context
-------
This package provides reusable data structures. Sequence[T] is a list-like
with modular slicing (wrap-around), shift, add/sub/and/invert, and
canonical hash; used by Polygon and geometry. Table[T] is a dict-like
keyed by hash(item), with add/pop and Serializable[dict]; used for
obstacles, ears, convex_components, guards, visibility in ArtGallery.
Both support serialize/unserialize for S3 and API.

Examples:
>>> from structs import Sequence, Table
>>> poly = Polygon(Sequence([p0, p1, p2]))
>>> table = Table().add(ear1).add(ear2)
"""

from structs.sequence import Sequence
from structs.table import Table

__all__ = ["Sequence", "Table"]
