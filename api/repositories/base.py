"""
Base repository and private repository for S3 persistence.
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
    UnauthorizedError,
    ValidationError,
)
from models import Model
from models import User

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
    >>> results = repo.search(next_token=request.get("next_token"), limit=20)
    """

    MODEL: ClassVar[type[Model]]

    @property
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError

    def get(self, identifier: Identifier | str) -> T:
        ident = Identifier(identifier) if isinstance(identifier, str) else identifier
        if not self.MODEL:
            raise ConfigurationError("MODEL is not set")
        data: Any = bucket.load(f"{self.path}/{ident}.json")
        if data is None:
            raise RecordNotFoundError(f"{ident} not found in {self.path}")
        if not isinstance(data, dict) or data.get("id") != ident:
            raise CorruptionError("ID mismatch in record")
        return cast(T, self.MODEL.from_dict(data))

    def save(self, record: T) -> T:
        if not self.MODEL:
            raise ConfigurationError("MODEL is not set")
        if not isinstance(record, self.MODEL):
            raise ValidationError(f"Object must be a {self.MODEL.__name__}")
        bucket.save(f"{self.path}/{record.id}.json", record.to_dict())
        return self.get(record.id)

    def delete(self, identifier: Identifier | str) -> None:
        ident = Identifier(identifier) if isinstance(identifier, str) else identifier
        bucket.delete(f"{self.path}/{ident}.json")

    def exists(self, identifier: Identifier | str) -> bool:
        ident = Identifier(identifier) if isinstance(identifier, str) else identifier
        return bucket.exists(f"{self.path}/{ident}.json")

    def search(
        self,
        next_token: str | None = None,
        limit: Limit | int = 20,
    ) -> Results[T]:
        if not self.MODEL:
            raise ConfigurationError("MODEL is not set")
        lim = Limit(limit) if not isinstance(limit, Limit) else limit
        results: Results[T] = Results()
        page: Page = bucket.search(
            f"{self.path}/",
            limit=lim,
            next_token=next_token,
        )
        for key in page:
            data = bucket.load(key)
            if data is None:
                raise RecordNotFoundError(f"{key} not found")
            results.records.append(cast(T, self.MODEL.from_dict(data)))
        results.next_token = page.next_token
        return results


@dataclass
class PrivateRepository(Repository[T], ABC):
    """
    Base for user-scoped repositories. Path uses the user email's slug (e.g. data/{email.slug}/jobs).

    Example:
    >>> repo = JobsRepository(user=request.user)
    >>> job = repo.get(job_id)
    """

    NAME: ClassVar[str]
    MODEL: ClassVar[type[Model]]
    user: User

    @property
    def path(self) -> str:
        """S3 prefix for this private repo: data/{email.slug}/{NAME}. Uses slug to avoid special characters in paths."""
        if not self.NAME:
            raise ConfigurationError("NAME is not set")
        if not self.user or not self.user.is_authenticated():
            raise UnauthorizedError("User is not authenticated")
        email = self.user.email
        if email is None:
            raise UnauthorizedError("User is not authenticated")
        return f"data/{email.slug}/{self.NAME}"
