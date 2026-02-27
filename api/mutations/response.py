"""
Mutation response: base TypedDict and mutation response subclasses.

Title
-----
Mutation Response Types

Context
-------
This module defines TypedDicts for mutation output. MutationResponse is
the base. ArtGalleryPublishMutationResponse and ArtGalleryHideMutationResponse
carry gallery data or deleted/id. JobMutationResponse and JobUpdateMutationResponse
carry full job dict. Handlers return these shapes (or compatible dicts)
which the interceptor JSON-serializes as the API response body. Used for
typing and documentation of API contract.

Examples:
    def mutate(self, validated_input) -> JobMutationResponse:
        return job.serialize()
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
    title: str
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
