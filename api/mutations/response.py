"""
Mutation response: base TypedDict and mutation response subclasses.
"""

from __future__ import annotations

from typing import Any
from typing import TypedDict


class MutationResponse(TypedDict):
    """Base for mutation outputs."""

    pass


class ArtGalleryPublishMutationResponse(MutationResponse):
    """Response: serialized gallery (ArtGalleryDict shape)."""

    id: str
    created_at: str
    updated_at: str
    boundary: list[Any]
    obstacles: dict[str, Any]
    owner_email: str
    owner_job_id: str
    ears: dict[str, Any]
    convex_components: dict[str, Any]
    guards: dict[str, Any]
    visibility: dict[str, Any]


class ArtGalleryHideMutationResponse(MutationResponse):
    """Response: deleted flag and gallery id."""

    deleted: bool
    id: str


class JobMutationResponse(MutationResponse):
    """Response: serialized job (JobDict shape)."""

    id: str
    created_at: str
    updated_at: str
    parent_id: str | None
    children_ids: list[str]
    status: str
    stage: str
    stdin: dict[str, Any]
    stdout: dict[str, Any]
    meta: dict[str, Any]
    stderr: dict[str, Any]
