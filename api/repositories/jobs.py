"""
Per-user jobs repository.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from models import Job
from models import Model
from models import User

from repositories.base import PrivateRepository


@dataclass
class JobsRepository(PrivateRepository[Job]):
    """
    Per-user job repository. Path: data/{email}/jobs.

    Example:
    >>> repo = JobsRepository(user=user)
    >>> repo.save(job)
    >>> job = repo.get(job.id)
    """

    NAME: ClassVar[str] = "jobs"
    MODEL: ClassVar[type[Model]] = Job
