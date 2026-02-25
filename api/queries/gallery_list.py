"""
Art gallery list query.
"""

from __future__ import annotations

from typing import Any

from attributes import Limit
from index.gallery import ArtGalleryPublicIndex

from queries.base import Query
from queries.request import QueryRequest
from queries.response import QueryResponse


class ArtGalleryListQueryRequest(QueryRequest, total=False):
    """Request for listing galleries."""

    next_token: str
    limit: Limit


class ArtGalleryListQueryResponse(QueryResponse):
    """Response for gallery list: records and next_token."""

    records: list[dict[str, Any]]
    next_token: str


class ArtGalleryListQuery(Query[ArtGalleryListQueryRequest, ArtGalleryListQueryResponse]):
    """List galleries using the public index."""

    def validate(self, body: dict[str, Any] | None = None) -> ArtGalleryListQueryRequest:
        payload = body or {}
        next_token = payload.get("next_token") or ""
        raw_limit = payload.get("limit")
        out: ArtGalleryListQueryRequest = {"next_token": next_token}
        if raw_limit is not None:
            out["limit"] = Limit(raw_limit)
        return out

    def query(self, validated_input: ArtGalleryListQueryRequest) -> ArtGalleryListQueryResponse:
        index = ArtGalleryPublicIndex()
        limit = validated_input.get("limit") or Limit(20)
        records, next_token = index.search(
            next_token=validated_input.get("next_token") or None,
            limit=limit,
        )
        return {
            "records": [record.serialize() for record in records],
            "next_token": next_token,
        }
