"""
Mutation request: base TypedDict and all mutation request subclasses.

Title
-----
Mutation Request Types

Context
-------
This module defines TypedDicts for mutation input. MutationRequest is
the base. ArtGalleryPublishMutationRequest and ArtGalleryHideMutationRequest
have job_id. JobMutationRequest has boundary and obstacles. JobUpdateMutationRequest
has job_id and meta. These types document the expected body shape after
validation and are used by Mutation subclasses in validate() return and
mutate() parameter. Path params (e.g. id) are merged into body by the
handler before validate.

Examples:
>>> def validate(self, body) -> JobMutationRequest:
>>> return JobMutationRequest(boundary=..., obstacles=...)
>>> def mutate(self, validated_input: ArtGalleryPublishMutationRequest): ...
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
