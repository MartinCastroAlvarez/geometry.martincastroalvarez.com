"""
Query handlers for art galleries and jobs.
"""

from queries.gallery_details import ArtGalleryDetailsQuery
from queries.gallery_list import ArtGalleryListQuery
from queries.job_details import JobDetailsQuery
from queries.job_list import JobListQuery

__all__ = [
    "ArtGalleryDetailsQuery",
    "ArtGalleryListQuery",
    "JobDetailsQuery",
    "JobListQuery",
]
