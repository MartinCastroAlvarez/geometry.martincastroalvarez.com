"""
Public index for art galleries (list by reversed created_at).

Title
-----
Art Gallery Public Index

Context
-------
ArtGalleryPublicIndex lists published galleries in newest-first order.
Path is index/galleries/. Index id is Countdown.from_timestamp(created_at)
so listing by key gives newest first. No user scope; public list and
detail queries use this index. REPOSITORY is ArtGalleryRepository so
get() and search() return ArtGallery instances. Used by ArtGalleryListQuery
and ArtGalleryPublishMutation (save) / ArtGalleryHideMutation (delete).

Examples:
>>> index = ArtGalleryPublicIndex()
>>> records, next_token = index.search(limit=Limit(20))
>>> gallery = index.get(Identifier(countdown_str))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import ClassVar

from indexes.base import Index
from repositories.gallery import ArtGalleryRepository


@dataclass
class ArtGalleryPublicIndex(Index[Any]):
    """
    Public index for art galleries. List returns galleries by reversed created_at.
    """

    REPOSITORY: ClassVar[type] = ArtGalleryRepository
    NAME: ClassVar[str] = "galleries"
