"""
Art gallery details query.
"""

from __future__ import annotations

from typing import Any

from repositories.gallery import ArtGalleryRepository
from attributes import Identifier

from queries.private import PrivateQuery
from queries.request import DetailsQueryRequest
from queries.response import DetailsQueryResponse


class ArtGalleryDetailsQueryResponse(DetailsQueryResponse):
    """Details response: single gallery (ArtGalleryDict shape)."""

    id: str
    boundary: list[Any]
    obstacles: dict[str, Any]
    owner_email: str
    owner_job_id: str
    created_at: str
    updated_at: str
    ears: dict[str, Any]
    convex_components: dict[str, Any]
    guards: dict[str, Any]
    visibility: dict[str, Any]


class ArtGalleryDetailsQuery(PrivateQuery[DetailsQueryRequest, ArtGalleryDetailsQueryResponse]):
    """Get a single gallery by id from the repository."""

    def _validate_body(self, body: dict[str, Any]) -> DetailsQueryRequest:
        return DetailsQueryRequest(id=Identifier(body.get("id")))

    def query(self, validated_input: DetailsQueryRequest) -> ArtGalleryDetailsQueryResponse:
        repo = ArtGalleryRepository()
        gallery = repo.get(validated_input["id"])
        return gallery.serialize()
