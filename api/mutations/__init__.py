"""
Mutations for art galleries and jobs.
"""

from mutations.gallery_publish import ArtGalleryPublishMutation
from mutations.gallery_unpublish import ArtGalleryHideMutation
from mutations.jobs import JobMutation

__all__ = [
    "ArtGalleryHideMutation",
    "ArtGalleryPublishMutation",
    "JobMutation",
]
