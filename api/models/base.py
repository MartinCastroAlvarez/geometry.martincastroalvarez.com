"""
Abstract Model base for persisted entities. id, created_at, updated_at; serialize/unserialize.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from attributes import Identifier
from attributes import Timestamp
from interfaces import Serializable


class Model(Serializable[dict[str, Any]]):
    """
    Abstract base for all persisted models. id (Identifier), created_at, updated_at are attributes.

    Example:
    >>> data = gallery.serialize()
    >>> gallery = ArtGallery.unserialize(data)
    """

    id: Identifier
    created_at: Timestamp
    updated_at: Timestamp

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def unserialize(cls, data: dict[str, Any]) -> Model:
        raise NotImplementedError

    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        raise NotImplementedError
