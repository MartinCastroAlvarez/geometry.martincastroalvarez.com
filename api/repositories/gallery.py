"""
Art gallery repository (public S3 path).
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
