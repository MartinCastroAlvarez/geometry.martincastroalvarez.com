"""
Query handlers for art galleries and jobs.
"""

from queries.galleries import ArtGalleryDetailsQuery
from queries.galleries import ArtGalleryListQuery
from queries.jobs import JobDetailsQuery
from queries.jobs import JobListQuery

__all__ = [
    "ArtGalleryDetailsQuery",
    "ArtGalleryListQuery",
    "JobDetailsQuery",
    "JobListQuery",
]
