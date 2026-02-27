"""
Abstract Model base for persisted entities. id, created_at, updated_at; serialize/unserialize.

Title
-----
Model Base Class

Context
-------
Model is the abstract base for all persisted entities. It defines id
(Identifier), created_at, updated_at (Timestamp), and requires
serialize() -> ModelDict and unserialize(data) -> Model. Subclasses
implement __str__, __repr__, and their own serialize/unserialize.
ModelDict is the TypedDict base for serialized shape. Hash is
Signature(id). Used by Repository, indexes, and all API payloads that
read or write gallery/job/user data.

Examples:
    data = gallery.serialize()
    gallery = ArtGallery.unserialize(data)
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any
from typing import TypedDict

from attributes import Identifier
from attributes import Signature
from attributes import Timestamp
from interfaces import Serializable


class ModelDict(TypedDict, total=False):
    """Base shape for serialized Model instances."""

    id: str
    created_at: str
    updated_at: str


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
