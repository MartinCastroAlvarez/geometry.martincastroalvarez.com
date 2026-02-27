"""
Indexes for listing records by sort key (e.g. Countdown).

Title
-----
Indexes Module

Context
-------
Indexes provide secondary listing by sort key (e.g. newest-first via
Countdown). Index and PrivateIndex define get, save, delete, exists,
search, and all; path is index/{NAME}/ or index/{NAME}/{email.slug}/.
ArtGalleryPublicIndex lists galleries by reversed created_at. JobsPrivateIndex
lists jobs per user. Indexed holds index_id (sort key) and real_id (record id).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import Iterator
from typing import TypedDict
from typing import TypeVar

from attributes import Email
from attributes import Identifier
from attributes import Limit
from attributes import Offset
from data import Bucket
from data import Page
from exceptions import RecordNotFoundError
from exceptions import ValidationError
from interfaces import Serializable
from repositories import ArtGalleryRepository
from repositories import JobsRepository
from serializers import Serialized

from api.settings import DEFAULT_LIMIT

bucket = Bucket()
T = TypeVar("T")


class IndexedDict(TypedDict):
    """Serialized form of Indexed (serialize/unserialize)."""

    index_id: str
    real_id: str


@dataclass
class Indexed(Serializable[dict[str, Any]]):
    """
    Stored index entry: index_id (sort key) and real_id (actual record id).

    For example, to create an index entry for a gallery:
    >>> entry = Indexed(index_id=Identifier("20240101"), real_id=Identifier("g1"))
    >>> entry.serialize()
    {'index_id': '20240101', 'real_id': 'g1'}
    """

    index_id: Identifier
    real_id: Identifier

    def serialize(self) -> IndexedDict:
        return {"index_id": str(self.index_id), "real_id": str(self.real_id)}

    @classmethod
    def unserialize(cls, data: Any) -> Indexed:
        if not isinstance(data, dict):
            raise ValidationError("Indexed data must be a dict")
        return cls(
            index_id=Identifier(data.get("index_id")),
            real_id=Identifier(data.get("real_id")),
        )


@dataclass
class Index(Generic[T]):
    """
    Generic index: stores Indexed entries under index/{NAME}/{index_id}.
    REPOSITORY is used to load the full record by real_id. Set REPOSITORY in subclass.

    For example, to list and get a gallery by index id:
    >>> index = ArtGalleryPublicIndex()
    >>> records, next_token = index.search(limit=Limit(20))
    >>> gallery = index.get(records[0].id)
    """

    REPOSITORY: ClassVar[type]
    NAME: ClassVar[str]

    @property
    def path(self) -> str:
        """S3 prefix for this index: index/{NAME}/."""
        return f"index/{self.NAME}/"

    @cached_property
    def repository(self) -> Any:
        """Repository instance used to load full records by real_id."""
        return self.REPOSITORY()

    def get(self, identifier: Identifier) -> Any:
        """
        Load the full record for an index entry by identifier.

        For example, to load a gallery by its index id (e.g. countdown):
        >>> gallery = index.get(Identifier("20240101120000"))
        >>> gallery.boundary
        Polygon(...)
        """
        data = bucket.load(f"{self.path}{identifier}.json")
        if data is None:
            raise RecordNotFoundError(f"Index entry {identifier} not found")
        indexed = Indexed.unserialize(data)
        return self.repository.get(indexed.real_id)

    def get_serialized(self, identifier: Identifier) -> Serialized:
        """
        Load the full record and return its serialized form (Serialized).

        For example, to get a gallery as a dict for API response:
        >>> data = index.get_serialized(Identifier("20240101120000"))
        >>> "boundary" in data
        True
        """
        return self.get(identifier).serialize()

    def save(self, record: Indexed) -> None:
        """
        Persist an index entry under this index path.

        For example, to add a gallery to the public index:
        >>> index.save(Indexed(index_id=Identifier(countdown), real_id=gallery.id))
        """
        if not isinstance(record, Indexed):
            raise ValidationError("record must be Indexed")
        bucket.save(f"{self.path}{record.index_id}.json", record.serialize())

    def delete(self, identifier: Identifier) -> bool:
        """
        Remove an index entry by identifier. Returns True if a key was deleted.

        For example, to remove a gallery from the public index:
        >>> index.delete(Identifier("20240101120000"))
        True
        """
        return bucket.delete(f"{self.path}{identifier}.json")

    def exists(self, identifier: Identifier) -> bool:
        """
        Return True if an index entry exists for the given identifier.

        For example, to check before deleting:
        >>> if index.exists(Identifier("20240101120000")):
        ...     index.delete(Identifier("20240101120000"))
        """
        return bucket.exists(f"{self.path}{identifier}.json")

    def search(
        self,
        next_token: Offset | None = None,
        limit: Limit = Limit(DEFAULT_LIMIT),
    ) -> tuple[list[Any], Offset | None]:
        """
        List index entries with pagination. Returns (records, next_token). Stale index keys are removed as read-repair.

        For example, to list newest galleries:
        >>> records, next_token = index.search(limit=Limit(20))
        >>> len(records)
        20
        """
        page: Page = bucket.search(
            prefix=self.path,
            limit=limit,
            next_token=next_token,
        )
        records: list[Any] = []
        for key in page:
            data = bucket.load(key)
            if data is None:
                bucket.delete(key)
                continue
            indexed = Indexed.unserialize(data)
            records.append(self.repository.get(indexed.real_id))
        return (records, page.next_token)

    def all(self) -> Iterator[Any]:
        """
        Iterate over all index entries (paginated internally). Stale index keys are removed as read-repair.

        For example, to iterate over every gallery in the index:
        >>> for gallery in index.all():
        ...     process(gallery)
        """
        next_token: Offset | None = None
        while True:
            page = bucket.search(
                prefix=self.path,
                limit=Limit(100),
                next_token=next_token,
            )
            for key in page:
                data = bucket.load(key)
                if data is None:
                    bucket.delete(key)
                    continue
                indexed = Indexed.unserialize(data)
                yield self.repository.get(indexed.real_id)
            if not page.continues:
                break
            next_token = page.next_token


@dataclass
class PrivateIndex(Index[T]):
    """
    Index scoped by user. path = index/{NAME}/{email.slug}/. Requires user for repository.

    For example, to list jobs for the current user:
    >>> index = JobsPrivateIndex(user_email=user.email)
    >>> records, next_token = index.search(limit=Limit(10))
    """

    user_email: Email

    @property
    def path(self) -> str:
        """S3 prefix for this private index: index/{NAME}/{email.slug}/."""
        return f"index/{self.NAME}/{self.user_email.slug}/"

    @cached_property
    def repository(self) -> Any:
        """Repository instance for this user, used to load full records by real_id."""
        from models import User

        user = User(email=self.user_email)
        return self.REPOSITORY(user=user)


@dataclass
class ArtGalleryPublicIndex(Index[Any]):
    """
    Public index for art galleries. List returns galleries by reversed created_at.

    For example, to list the newest galleries:
    >>> index = ArtGalleryPublicIndex()
    >>> galleries, token = index.search(limit=Limit(10))
    """

    REPOSITORY: ClassVar[type] = ArtGalleryRepository
    NAME: ClassVar[str] = "galleries"


@dataclass
class JobsPrivateIndex(PrivateIndex[Any]):
    """
    Per-user index for jobs.

    For example, to list the current user's jobs:
    >>> index = JobsPrivateIndex(user_email=user.email)
    >>> jobs, token = index.search(limit=Limit(20))
    """

    REPOSITORY: ClassVar[type] = JobsRepository
    NAME: ClassVar[str] = "jobs"
