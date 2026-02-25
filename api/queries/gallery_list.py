"""
Art gallery list query.
"""

from __future__ import annotations

from typing import Any

from attributes import Limit
from index.gallery import ArtGalleryPublicIndex

from queries.base import Query
from queries.base import QueryInput


class ArtGalleryListQueryInput(QueryInput, total=False):
    """Input for listing galleries."""

    next_token: str
    limit: Limit | int


class ArtGalleryListQuery(Query[ArtGalleryListQueryInput]):
    """List galleries using the public index."""

    def validate(self, body: dict[str, Any] | None = None) -> ArtGalleryListQueryInput:
        payload = body or {}
        next_token = payload.get("next_token") or ""
        raw_limit = payload.get("limit")
        out: ArtGalleryListQueryInput = {"next_token": next_token}
        if raw_limit is not None:
            out["limit"] = Limit(raw_limit)
        return out

    def query(self, validated_input: ArtGalleryListQueryInput) -> dict[str, Any]:
        index = ArtGalleryPublicIndex()
        limit = validated_input.get("limit") or Limit(20)
        records, next_token = index.search(
            next_token=validated_input.get("next_token") or None,
            limit=limit,
        )
        return {
            "records": [record.to_dict() for record in records],
            "next_token": next_token,
        }
