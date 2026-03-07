"""
Repositories for ArtGallery and Job persistence in S3.

Title
-----
Repositories Module

Context
-------
This module provides S3-backed persistence for ArtGallery and Job.
Repository is the base; PrivateRepository scopes path by user (data/{email.slug}/{NAME}).
ArtGalleryRepository is public (data/galleries). JobsRepository is
PrivateRepository (data/{email.slug}/jobs). Results holds paginated
search results (records, next_token). Used by mutations, queries,
indexes (to load full record by real_id), and worker tasks.

**List responses and 404:** When building list responses (e.g. from index
entries), callers that load records by id should catch RecordNotFoundError
(or check for missing data) and skip the item, performing read-repair by
deleting stale index entries when the underlying record is gone.

Examples:
>>> from repositories import ArtGalleryRepository, JobsRepository, Results
>>> repo = ArtGalleryRepository()
>>> job_repo = JobsRepository(user=user)
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import Iterator
from typing import TypeVar
from typing import cast

from attributes import Identifier
from attributes import Limit
from attributes import Offset
from attributes import Timestamp
from data import Bucket
from data import Page
from exceptions import ConfigurationError
from exceptions import CorruptionError
from exceptions import RecordNotFoundError
from exceptions import UnauthorizedError
from exceptions import ValidationError
from logger import get_logger
from models import ArtGallery
from models import Job
from models import JobState
from models import Model
from models import User
from settings import DEFAULT_LIMIT

bucket: Bucket = Bucket()
logger = get_logger(__name__)
T = TypeVar("T", bound=Model)


@dataclass
class Results(Generic[T]):
    """
    Paginated results from a repository search.

    For example, to iterate over search results:
    >>> results = repo.search(limit=Limit(10))
    >>> for record in results:
    ...     print(record.id)
    >>> next_token = results.next_token
    """

    records: list[T] = field(default_factory=list)
    next_token: Offset | None = None

    def __iter__(self) -> Iterator[T]:
        return iter(self.records)

    def __len__(self) -> int:
        return len(self.records)

    def serialize(self) -> dict[str, Any]:
        return {
            "records": [r.serialize() for r in self.records],
            "next_token": str(self.next_token) if self.next_token else "",
        }


@dataclass
class Repository(Generic[T], ABC):
    """
    Base repository. No versioning checks. Path and MODEL are defined by subclasses.

    For example, to load and save a record:
    >>> repo = ArtGalleryRepository()
    >>> gallery = repo.get(Identifier("abc"))
    >>> repo.save(gallery)
    """

    MODEL: ClassVar[type[Model]]

    @property
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError

    def get(self, identifier: Identifier) -> T:
        """
        Load a record by identifier. Raises RecordNotFoundError if not found.

        For example, to load a gallery by id:
        >>> gallery = repo.get(Identifier("gallery-123"))
        >>> gallery.boundary
        Polygon(...)
        """
        if not self.MODEL:
            raise ConfigurationError("MODEL is not set")
        key: str = f"{self.path}/{identifier}.json"
        data: Any = bucket.load(key)
        if data is None:
            logger.debug("Repository.get() | record not found path=%s id=%s", self.path, identifier)
            raise RecordNotFoundError(f"{identifier} not found in {self.path}")
        if not isinstance(data, dict) or data.get("id") != identifier:
            raise CorruptionError("ID mismatch in record")
        return cast(T, self.MODEL.unserialize(data))

    def save(self, record: T) -> T:
        """
        Persist a record and return the loaded instance.

        For example, to save a new job:
        >>> job = Job(id=Identifier("j1"), stdin={"boundary": [...]})
        >>> saved = repo.save(job)
        """
        if not self.MODEL:
            raise ConfigurationError("MODEL is not set")
        if not isinstance(record, self.MODEL):
            raise ValidationError(f"Object must be a {self.MODEL.__name__}")
        record.updated_at = Timestamp.now()
        key: str = f"{self.path}/{record.id}.json"
        bucket.save(key, record.serialize())
        logger.debug("Repository.save() | path=%s id=%s", self.path, record.id)
        return self.get(record.id)

    def delete(self, identifier: Identifier) -> None:
        """
        Delete a record by identifier.

        For example, to remove a gallery:
        >>> repo.delete(Identifier("gallery-123"))
        """
        bucket.delete(f"{self.path}/{identifier}.json")
        logger.debug("Repository.delete() | path=%s id=%s", self.path, identifier)

    def exists(self, identifier: Identifier) -> bool:
        """
        Return True if a record exists for the given identifier.

        For example, to check before updating:
        >>> if repo.exists(Identifier("g1")):
        ...     gallery = repo.get(Identifier("g1"))
        """
        return bucket.exists(f"{self.path}/{identifier}.json")

    def search(
        self,
        next_token: Offset | None = None,
        limit: Limit = Limit(DEFAULT_LIMIT),
    ) -> Results[T]:
        """
        List records with pagination. Returns Results with records and next_token.

        For example, to list galleries with a limit:
        >>> results = repo.search(limit=Limit(20))
        >>> len(results.records)
        20
        >>> results.next_token
        Offset('...') or None
        """
        if not self.MODEL:
            raise ConfigurationError("MODEL is not set")
        results: Results[T] = Results()
        page: Page = bucket.search(
            f"{self.path}/",
            limit=limit,
            next_token=next_token,
        )
        for key in page:
            data: Any = bucket.load(key)
            if data is None:
                continue
            results.records.append(cast(T, self.MODEL.unserialize(data)))
        results.next_token = page.next_token
        return results


@dataclass
class PrivateRepository(Repository[T], ABC):
    """
    Base for user-scoped repositories. Path uses the user email's slug (e.g. data/{email.slug}/jobs).

    For example, to create a per-user job repository:
    >>> repo = JobsRepository(user=request.user)
    >>> repo.path
    'data/user-abc123/jobs'
    """

    NAME: ClassVar[str]
    MODEL: ClassVar[type[Model]]
    user: User

    @property
    def path(self) -> str:
        """
        S3 prefix for this private repo: data/{email.slug}/{NAME}. Uses slug to avoid special characters in paths.

        For example, to get the storage path:
        >>> repo = JobsRepository(user=user)
        >>> repo.path
        'data/alice-123abc/jobs'
        """
        if not self.NAME:
            raise ConfigurationError("NAME is not set")
        if not self.user or not self.user.is_authenticated():
            raise UnauthorizedError("User is not authenticated")
        return f"data/{self.user.email.slug}/{self.NAME}"


@dataclass
class ArtGalleryRepository(Repository[ArtGallery]):
    """
    Public repository for art galleries. Path: data/galleries.

    For example, to list and get galleries:
    >>> repo = ArtGalleryRepository()
    >>> results = repo.search(limit=Limit(10))
    >>> gallery = repo.get(Identifier("g1"))
    """

    MODEL: ClassVar[type[Model]] = ArtGallery

    @property
    def path(self) -> str:
        return "data/galleries"


@dataclass
class JobsRepository(PrivateRepository[Job]):
    """
    Per-user job repository. Path: data/{email}/jobs.

    For example, to create and save a job for the current user:
    >>> repo = JobsRepository(user=user)
    >>> job = Job(id=Identifier("j1"), stdin={"boundary": [...]})
    >>> repo.save(job)
    """

    NAME: ClassVar[str] = "jobs"
    MODEL: ClassVar[type[Model]] = Job


@dataclass
class JobStateRepository(PrivateRepository[JobState]):
    """
    Per-user job state repository. Path: data/{email}/states.
    The state id equals the job id (1:1 relationship).

    For example, to create and save job state for the current user:
    >>> repo = JobStateRepository(user=user)
    >>> state = JobState(id=job.id, data={"key": "value"})
    >>> repo.save(state)
    """

    NAME: ClassVar[str] = "states"
    MODEL: ClassVar[type[Model]] = JobState
