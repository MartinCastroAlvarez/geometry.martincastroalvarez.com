"""
Art gallery repository (public S3 path).

Title
-----
ArtGallery Repository

Context
-------
ArtGalleryRepository persists ArtGallery records under data/galleries/
with key {id}.json. No user scope; any caller can get/save/delete by
id. Used by ArtGalleryPublishMutation, ArtGalleryHideMutation,
ArtGalleryDetailsQuery, ArtGalleryListQuery (via index.get), and
JobUpdateMutation (when syncing gallery title). MODEL is ArtGallery.

Examples:
    repo = ArtGalleryRepository()
    gallery = repo.get(Identifier("gallery_abc"))
    repo.save(gallery)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from models import ArtGallery
from models import Model
from repositories.base import Repository


@dataclass
class ArtGalleryRepository(Repository[ArtGallery]):
    """
    Public repository for art galleries. Path: data/galleries.

    Example:
    >>> repo = ArtGalleryRepository()
    >>> gallery = repo.get("gallery_abc")
    >>> repo.save(gallery)
    """

    MODEL: ClassVar[type[Model]] = ArtGallery

    @property
    def path(self) -> str:
        return "data/galleries"
