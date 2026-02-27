"""
Mutations for art galleries and jobs.

Title
-----
Mutations Package

Context
-------
This package exports write-side handlers: JobMutation (create job),
JobUpdateMutation (update job meta, sync title to gallery), ArtGalleryPublishMutation
(publish gallery from finished job), ArtGalleryHideMutation (remove gallery).
All gallery and job mutations that require auth use PrivateMutation and
receive request.user. Mutations validate body, mutate state (repo, index,
queue), and return a response dict. Registered in api.api.urls by path and method.

Examples:
    from mutations import JobMutation, ArtGalleryPublishMutation
    handler = JobMutation(user=request.user)
    result = handler.handle(body)
"""

from mutations.galleries import ArtGalleryHideMutation
from mutations.galleries import ArtGalleryPublishMutation
from mutations.jobs import JobMutation
from mutations.jobs import JobUpdateMutation

__all__ = [
    "ArtGalleryHideMutation",
    "ArtGalleryPublishMutation",
    "JobMutation",
    "JobUpdateMutation",
]
