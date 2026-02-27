"""
Repositories for ArtGallery and Job persistence in S3.

Title
-----
Repositories Package

Context
-------
This package provides S3-backed persistence for ArtGallery and Job.
Repository is the base; PrivateRepository scopes path by user (data/{email.slug}/{NAME}).
ArtGalleryRepository is public (data/galleries). JobsRepository is
PrivateRepository (data/{email.slug}/jobs). Results holds paginated
search results (records, next_token). Used by mutations, queries,
indexes (to load full record by real_id), and worker tasks.

Examples:
    from repositories import ArtGalleryRepository, JobsRepository, Results
    repo = ArtGalleryRepository()
    job_repo = JobsRepository(user=user)
"""

from repositories.base import Repository
from repositories.gallery import ArtGalleryRepository
from repositories.jobs import JobsRepository
from repositories.private import PrivateRepository
from repositories.results import Results

__all__ = [
    "ArtGalleryRepository",
    "JobsRepository",
    "PrivateRepository",
    "Repository",
    "Results",
]
