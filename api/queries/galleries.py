"""
Art gallery list and gallery details queries.

Title
-----
Art Gallery Queries

Context
-------
ArtGalleryListQuery lists published galleries via ArtGalleryPublicIndex
(newest first); returns records and next_token. ArtGalleryDetailsQuery
loads a single gallery by id from ArtGalleryRepository. Both are public
(no auth). Used for GET v1/galleries (list) and GET v1/galleries/:id
(details). Response records are serialized ArtGallery dicts.

Examples:
>>> GET v1/galleries?limit=20 -> ArtGalleryListQuery
>>> GET v1/galleries/:id -> ArtGalleryDetailsQuery
"""

from __future__ import annotations

from indexes.gallery import ArtGalleryPublicIndex
from queries.base import DetailsQuery
from queries.base import ListQuery
from queries.request import DetailsQueryRequest
from queries.request import ListQueryRequest
from queries.response import ListQueryResponse
from repositories import ArtGalleryRepository
from serializers import Serialized


class ArtGalleryListQuery(ListQuery):
    """List galleries using the public index. Public query; no user check."""

    def query(self, validated_input: ListQueryRequest) -> ListQueryResponse:
        index = ArtGalleryPublicIndex()
        records, next_token = index.search(
            next_token=validated_input.get("next_token"),
            limit=validated_input["limit"],
        )
        return {
            "records": [record.serialize() for record in records],
            "next_token": str(next_token) if next_token else "",
        }


class ArtGalleryDetailsQuery(DetailsQuery):
    """Get a single gallery by id from the repository. Public query; no user check."""

    def query(self, validated_input: DetailsQueryRequest) -> Serialized:
        repo = ArtGalleryRepository()
        gallery = repo.get(validated_input["id"])
        return gallery.serialize()
