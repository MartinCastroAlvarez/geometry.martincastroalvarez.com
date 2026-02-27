"""
Query handlers for art galleries and jobs.

Title
-----
Queries Package

Context
-------
This package exports read-side handlers: ArtGalleryListQuery, ArtGalleryDetailsQuery,
JobListQuery, JobDetailsQuery. List queries use indexes (ArtGalleryPublicIndex,
JobsPrivateIndex) and return records + next_token. Details queries use
repositories and require id (from path). Job queries use PrivateQuery
(user must be authenticated); gallery list/details are public. Registered
in api.api.urls. All return dicts that the interceptor JSON-serializes.

Examples:
>>> from queries import ArtGalleryListQuery, JobDetailsQuery
>>> query = ArtGalleryListQuery()
>>> result = query.handle(body={"limit": 20})
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
