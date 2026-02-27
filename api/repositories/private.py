"""
Private (user-scoped) repository base for S3 persistence.

Title
-----
PrivateRepository Base Class

Context
-------
PrivateRepository extends Repository and scopes the S3 path by user:
path = data/{user.email.slug}/{NAME}. Subclasses set NAME and MODEL.
User must be authenticated (is_authenticated()); otherwise path getter
raises UnauthorizedError. Used by JobsRepository so each user's jobs
are stored under their email slug. Index and repository use the same
user for consistency.

Examples:
    class JobsRepository(PrivateRepository[Job]):
        NAME = "jobs"
        MODEL = Job
    repo = JobsRepository(user=request.user)
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import ClassVar
from typing import TypeVar

from exceptions import ConfigurationError
from exceptions import UnauthorizedError
from models import Model
from models import User
from repositories.base import Repository

T = TypeVar("T", bound=Model)


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
        return f"data/{self.user.email.slug}/{self.NAME}"
