"""
Indexes for listing records by sort key (e.g. Countdown).

Title
-----
Indexes Package

Context
-------
Indexes provide secondary listing by sort key (e.g. newest-first via
Countdown). Index and PrivateIndex in base define get, save, delete,
exists, search, and all; path is index/{NAME}/ or index/{NAME}/{email.slug}/.
ArtGalleryPublicIndex lists galleries by reversed created_at. JobsPrivateIndex
lists jobs per user. Indexed holds index_id (sort key) and real_id (record id).
Stale index entries (missing data) are read-repaired on search/all. Repository
is used to load full records by real_id.

Examples:
    index = ArtGalleryPublicIndex()
    records, next_token = index.search(limit=Limit(10))
    index = JobsPrivateIndex(user_email=user.email)
"""

from indexes.base import Index
from indexes.base import PrivateIndex
from indexes.gallery import ArtGalleryPublicIndex
from indexes.indexed import Indexed
from indexes.jobs import JobsPrivateIndex

__all__ = [
    "ArtGalleryPublicIndex",
    "Index",
    "Indexed",
    "JobsPrivateIndex",
    "PrivateIndex",
]
