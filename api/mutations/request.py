"""
Mutation request: base TypedDict and all mutation request subclasses.
"""

from __future__ import annotations

from typing import TypedDict

from attributes import Identifier
from geometry import Polygon
from structs import Table


class MutationRequest(TypedDict):
    """Base for mutation requests."""

    pass


class ArtGalleryPublishMutationRequest(MutationRequest):
    """Publish: job_id required; gallery data taken from job stdout."""

    job_id: Identifier


class ArtGalleryHideMutationRequest(MutationRequest):
    """Hide: job_id required; gallery id derived from job id + hash(user email)."""

    job_id: Identifier


class JobMutationRequest(MutationRequest):
    """Create job: boundary and obstacles; id is hash (idempotent)."""

    boundary: Polygon
    obstacles: Table[Polygon]


class JobUpdateMutationRequest(MutationRequest):
    """Update job: job_id from path; metadata only."""

    job_id: Identifier
    meta: dict[str, str]
