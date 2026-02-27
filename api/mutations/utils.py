"""
Shared helpers for mutations.

Title
-----
Mutation Utilities

Context
-------
gallery_id_from_job_and_user(job_id, user_email) returns a stable
Identifier for the gallery associated with a job and owner: it is
Identifier(Signature(f"{job_id}_{user_email}")). This ensures the same
user and job always map to the same gallery id for publish/hide and
for repository lookups. Used by ArtGalleryPublishMutation, ArtGalleryHideMutation,
and JobUpdateMutation (to find gallery by job and user when syncing title).

Examples:
    gallery_id = gallery_id_from_job_and_user(job.id, user.email)
    gallery_repo.get(gallery_id)
"""

from __future__ import annotations

from attributes import Email
from attributes import Identifier
from attributes import Signature


def gallery_id_from_job_and_user(job_id: Identifier, user_email: Email) -> Identifier:
    """Stable gallery id: Identifier of the Signature of the concatenation of job_id and user_email."""
    return Identifier(Signature(f"{job_id}_{user_email}"))
