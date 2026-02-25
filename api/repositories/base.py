"""
Base repository for S3 persistence.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import TypeVar
from typing import cast

from data import Bucket
from data import Page
from exceptions import (
    ConfigurationError,
    CorruptionError,
    RecordNotFoundError,
    ValidationError,
)
from models import Model

from attributes import Identifier
from attributes import Limit
from repositories.results import Results

bucket = Bucket()
T = TypeVar("T", bound=Model)


@dataclass
class Repository(Generic[T], ABC):
    """
    Base repository. No versioning checks. Path and MODEL are defined by subclasses.

    Example:
    >>> repo = ArtGalleryRepository()
    >>> gallery = repo.get("gallery_id")
    >>> repo.save(gallery)
    >>> results = repo.search(next_token=request.get("next_token"), limit=Limit(20))
    """

    MODEL: ClassVar[type[Model]]

    @property
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError

    def get(self, identifier: Identifier) -> T:
        if not self.MODEL:
            raise ConfigurationError("MODEL is not set")
        data: Any = bucket.load(f"{self.path}/{identifier}.json")
        if data is None:
            raise RecordNotFoundError(f"{identifier} not found in {self.path}")
        if not isinstance(data, dict) or data.get("id") != identifier:
            raise CorruptionError("ID mismatch in record")
        return cast(T, self.MODEL.unserialize(data))

    def save(self, record: T) -> T:
        if not self.MODEL:
            raise ConfigurationError("MODEL is not set")
        if not isinstance(record, self.MODEL):
            raise ValidationError(f"Object must be a {self.MODEL.__name__}")
        bucket.save(f"{self.path}/{record.id}.json", record.serialize())
        return self.get(record.id)

    def delete(self, identifier: Identifier) -> None:
        bucket.delete(f"{self.path}/{identifier}.json")

    def exists(self, identifier: Identifier) -> bool:
        return bucket.exists(f"{self.path}/{identifier}.json")

    def search(
        self,
        next_token: str | None = None,
        limit: Limit = Limit(20),
    ) -> Results[T]:
        if not self.MODEL:
            raise ConfigurationError("MODEL is not set")
        results: Results[T] = Results()
        page: Page = bucket.search(
            f"{self.path}/",
            limit=limit,
            next_token=next_token,
        )
        for key in page:
            data = bucket.load(key)
            if data is None:
                continue
            results.records.append(cast(T, self.MODEL.unserialize(data)))
        results.next_token = page.next_token
        return results
