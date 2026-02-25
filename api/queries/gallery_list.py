"""
Art gallery list query.
"""

from __future__ import annotations

from typing import Any

from attributes import Limit
from attributes import Offset
from indexes.gallery import ArtGalleryPublicIndex
from models.gallery import ArtGalleryDict

from queries.base import Query
from queries.request import ListQueryRequest
from queries.response import ListQueryResponse


class ArtGalleryListQueryResponse(ListQueryResponse):
    """List response with gallery records."""

    records: list[ArtGalleryDict]


class ArtGalleryListQuery(Query[ListQueryRequest, ArtGalleryListQueryResponse]):
    """List galleries using the public index. Public query; no user check."""

    def validate(self, body: dict[str, Any]) -> ListQueryRequest:
        return {
            "next_token": Offset(body.get("next_token")) if body.get("next_token") is not None else None,
            "limit": Limit(body.get("limit")) if body.get("limit") is not None else Limit(20),
        }

    def query(self, validated_input: ListQueryRequest) -> ArtGalleryListQueryResponse:
        index = ArtGalleryPublicIndex()
        limit = validated_input["limit"]
        records, next_token = index.search(
            next_token=validated_input.get("next_token"),
            limit=limit,
        )
        return {
            "records": [record.serialize() for record in records],
            "next_token": str(next_token) if next_token else "",
        }
