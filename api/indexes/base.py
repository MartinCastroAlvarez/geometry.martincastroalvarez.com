"""
Generic Index and PrivateIndex for S3-backed listing by sort key.

Title
-----
Index Base Classes

Context
-------
Index is a generic S3-backed index: entries are stored under index/{NAME}/
as {index_id}.json containing Indexed (index_id, real_id). REPOSITORY
loads the full record by real_id. get(identifier) returns the record;
search(next_token, limit) returns (records, next_token) with read-repair
for stale keys. PrivateIndex scopes path to index/{NAME}/{email.slug}/ and
requires user for repository. Subclasses set NAME and REPOSITORY. Used by
ArtGalleryPublicIndex and JobsPrivateIndex.

Examples:
>>> index = ArtGalleryPublicIndex()
>>> records, next_token = index.search(limit=Limit(10))
>>> record = index.get(Identifier("gallery-123"))
>>> index.save(Indexed(index_id=key, real_id=record.id))
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import Iterator
from typing import TypeVar

from attributes import Email
from attributes import Identifier
from attributes import Limit
from attributes import Offset
from data import Bucket
from data import Page
from exceptions import RecordNotFoundError
from exceptions import ValidationError
from indexes.indexed import Indexed
from models.base import ModelDict

bucket = Bucket()
T = TypeVar("T")


@dataclass
class Index(Generic[T]):
    """
    Generic index: stores Indexed entries under index/{NAME}/{index_id}.
    REPOSITORY is used to load the full record by real_id. Set REPOSITORY in subclass.
    Records loaded via get() have serialize() -> ModelDict.

    Example:
    >>> index = ArtGalleryPublicIndex()
    >>> records, next_token = index.search(limit=Limit(10))
    >>> record = index.get(index_id)
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

        Example:
        >>> index = ArtGalleryPublicIndex()
        >>> gallery = index.get(Identifier("gallery-123"))
        """
        data = bucket.load(f"{self.path}{identifier}.json")
        if data is None:
            raise RecordNotFoundError(f"Index entry {identifier} not found")
        indexed = Indexed.unserialize(data)
        return self.repository.get(indexed.real_id)

    def get_serialized(self, identifier: Identifier) -> ModelDict:
        """Load the full record and return its serialized form (ModelDict)."""
        return self.get(identifier).serialize()

    def save(self, record: Indexed) -> None:
        """
        Persist an index entry under this index path.

        Example:
        >>> index = ArtGalleryPublicIndex()
        >>> index.save(Indexed(index_id="gallery-123", real_id="abc"))
        """
        if not isinstance(record, Indexed):
            raise ValidationError("record must be Indexed")
        bucket.save(f"{self.path}{record.index_id}.json", record.serialize())

    def delete(self, identifier: Identifier) -> bool:
        """
        Remove an index entry by identifier. Returns True if a key was deleted.

        Example:
        >>> index = ArtGalleryPublicIndex()
        >>> index.delete(Identifier("gallery-123"))
        True
        """
        return bucket.delete(f"{self.path}{identifier}.json")

    def exists(self, identifier: Identifier) -> bool:
        """
        Return True if an index entry exists for the given identifier.

        Example:
        >>> index = ArtGalleryPublicIndex()
        >>> index.exists(Identifier("gallery-123"))
        False
        """
        return bucket.exists(f"{self.path}{identifier}.json")

    def search(
        self,
        next_token: Offset | None = None,
        limit: Limit = Limit(20),
    ) -> tuple[list[Any], Offset | None]:
        """
        List index entries with pagination. Returns (records, next_token).
        Stale index keys (missing data) are removed as read-repair and skipped.

        Example:
        >>> index = ArtGalleryPublicIndex()
        >>> records, next_token = index.search(limit=Limit(10))
        >>> records, next_token = index.search(next_token=next_token, limit=Limit(10))
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
                # Read-repair: index key exists but indexed data is missing; delete stale key.
                bucket.delete(key)
                continue
            indexed = Indexed.unserialize(data)
            records.append(self.repository.get(indexed.real_id))
        return (records, page.next_token)

    def all(self) -> Iterator[Any]:
        """
        Iterate over all index entries (paginated internally). Stale index keys
        (missing data) are removed as read-repair and skipped.

        Example:
        >>> index = ArtGalleryPublicIndex()
        >>> for gallery in index.all():
        ...     print(gallery.id)
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
                    # Read-repair: index key exists but indexed data is missing; delete stale key.
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

    Example:
    >>> index = JobsPrivateIndex(user_email=Email("user@example.com"))
    >>> records, next_token = index.search(limit=Limit(20))
    """

    user_email: Email

    @property
    def path(self) -> str:
        """S3 prefix for this private index: index/{NAME}/{email.slug}/. Uses slug to avoid special characters in paths."""
        return f"index/{self.NAME}/{self.user_email.slug}/"

    @cached_property
    def repository(self) -> Any:
        """Repository instance for this user, used to load full records by real_id."""
        from models import User

        user = User(email=self.user_email)
        return self.REPOSITORY(user=user)
