"""
Per-user index for jobs.

Title
-----
Jobs Private Index

Context
-------
JobsPrivateIndex lists jobs for a single user in newest-first order. Path
is index/jobs/{email.slug}/. Index id is Countdown.from_timestamp(job.created_at).
REPOSITORY is JobsRepository(user=user). Used by JobListQuery and
JobMutation (save to index after create). Only the owning user can list
or access their jobs via this index.

Examples:
>>> index = JobsPrivateIndex(user_email=Email("user@example.com"))
>>> records, next_token = index.search(limit=Limit(20))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import ClassVar

from indexes.base import PrivateIndex
from repositories.jobs import JobsRepository


@dataclass
class JobsPrivateIndex(PrivateIndex[Any]):
    """
    Per-user index for jobs.
    """

    REPOSITORY: ClassVar[type] = JobsRepository
    NAME: ClassVar[str] = "jobs"
