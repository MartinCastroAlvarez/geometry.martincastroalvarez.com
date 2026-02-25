"""
Art gallery details query.
"""

from __future__ import annotations

from typing import Any

from exceptions import ValidationError
from repositories.gallery import ArtGalleryRepository

from queries.base import Query
from queries.base import QueryInput


class ArtGalleryDetailsQueryInput(QueryInput):
    """Input for gallery by id."""

    id: str


class ArtGalleryDetailsQuery(Query[ArtGalleryDetailsQueryInput]):
    """Get a single gallery by id from the repository."""

    def validate(self, body: dict[str, Any] | None = None) -> ArtGalleryDetailsQueryInput:
        payload = body or {}
        identifier = payload.get("id")
        if not identifier or not isinstance(identifier, str):
            raise ValidationError("id is required and must be a non-empty string")
        return ArtGalleryDetailsQueryInput(id=identifier)

    def query(self, validated_input: ArtGalleryDetailsQueryInput) -> dict[str, Any]:
        repo = ArtGalleryRepository()
        gallery = repo.get(validated_input["id"])
        return gallery.to_dict()
