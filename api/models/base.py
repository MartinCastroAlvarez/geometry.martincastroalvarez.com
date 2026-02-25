"""
Abstract Model base for persisted entities. id, created_at, updated_at; to_dict/from_dict.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from attributes import Identifier
from interfaces import Serializable
from attributes import Timestamp


class Model(Serializable):
    """
    Abstract base for all persisted models. id (Identifier), created_at, updated_at are attributes.

    Example:
    >>> data = gallery.to_dict()
    >>> gallery = ArtGallery.from_dict(data)
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
    def from_dict(cls, data: dict[str, Any]) -> Model:
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError
