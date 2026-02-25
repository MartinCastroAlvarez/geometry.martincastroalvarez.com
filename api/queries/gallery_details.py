"""
Art gallery details query.
"""

from __future__ import annotations

from typing import Any

from repositories.gallery import ArtGalleryRepository
from attributes import Identifier

from queries.base import Query
from queries.request import QueryRequest
from queries.response import QueryResponse


class ArtGalleryDetailsQueryRequest(QueryRequest):
    """Request for gallery by id."""

    id: Identifier


class ArtGalleryDetailsQueryResponse(QueryResponse):
    """Response for gallery details: single gallery dict."""

    id: str
    boundary: list[Any]
    obstacles: list[Any]
    owner_email: str
    owner_job_id: str
    created_at: str
    updated_at: str
    ears: list[Any]
    convex_components: list[Any]
    guards: list[Any]
    visibility: dict[str, Any]


class ArtGalleryDetailsQuery(Query[ArtGalleryDetailsQueryRequest, ArtGalleryDetailsQueryResponse]):
    """Get a single gallery by id from the repository."""

    def validate(self, body: dict[str, Any] | None = None) -> ArtGalleryDetailsQueryRequest:
        payload = body or {}
        return ArtGalleryDetailsQueryRequest(id=Identifier(payload.get("id")))

    def query(self, validated_input: ArtGalleryDetailsQueryRequest) -> ArtGalleryDetailsQueryResponse:
        repo = ArtGalleryRepository()
        gallery = repo.get(validated_input["id"])
        return gallery.serialize()
