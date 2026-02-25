"""
Public index for art galleries (list by reversed created_at).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import ClassVar

from repositories.gallery import ArtGalleryRepository

from indexes.base import Index


@dataclass
class ArtGalleryPublicIndex(Index[Any]):
    """
    Public index for art galleries. List returns galleries by reversed created_at.
    """

    REPOSITORY: ClassVar[type] = ArtGalleryRepository
    NAME: ClassVar[str] = "galleries"
