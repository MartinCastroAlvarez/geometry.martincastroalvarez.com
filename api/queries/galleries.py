"""
Art gallery list and gallery details queries.
"""

from __future__ import annotations

from indexes.gallery import ArtGalleryPublicIndex
from models.gallery import ArtGalleryDict
from queries.base import DetailsQuery
from queries.base import ListQuery
from queries.private import PrivateQuery
from queries.request import DetailsQueryRequest
from queries.request import ListQueryRequest
from queries.response import DetailsQueryResponse
from queries.response import ListQueryResponse
from repositories.gallery import ArtGalleryRepository


class ArtGalleryListQuery(ListQuery[ListQueryResponse[ArtGalleryDict]]):
    """List galleries using the public index. Public query; no user check."""

    def query(self, validated_input: ListQueryRequest) -> ListQueryResponse[ArtGalleryDict]:
        index = ArtGalleryPublicIndex()
        records, next_token = index.search(
            next_token=validated_input.get("next_token"),
            limit=validated_input["limit"],
        )
        return {
            "records": [record.serialize() for record in records],
            "next_token": str(next_token) if next_token else "",
        }


class ArtGalleryDetailsQuery(
    PrivateQuery[DetailsQueryRequest, DetailsQueryResponse[ArtGalleryDict]],
    DetailsQuery[DetailsQueryResponse[ArtGalleryDict]],
):
    """Get a single gallery by id from the repository."""

    def query(self, validated_input: DetailsQueryRequest) -> DetailsQueryResponse[ArtGalleryDict]:
        repo = ArtGalleryRepository()
        gallery = repo.get(validated_input["id"])
        return gallery.serialize()
