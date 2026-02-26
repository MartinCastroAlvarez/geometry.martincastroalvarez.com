"""
Mutations for art galleries and jobs.
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
