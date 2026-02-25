"""
Abstract Model base for persisted entities. id, created_at, updated_at; serialize/unserialize.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from attributes import Identifier
from attributes import Signature
from attributes import Timestamp
from interfaces import ModelDict
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

    def __hash__(self) -> Signature:
        return Signature(self.id)

    @classmethod
    @abstractmethod
    def unserialize(cls, data: dict[str, Any]) -> Model:
        raise NotImplementedError

    @abstractmethod
    def serialize(self) -> ModelDict:
        raise NotImplementedError
