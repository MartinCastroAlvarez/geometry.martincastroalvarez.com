"""
Per-user jobs repository.

Title
-----
Jobs Repository

Context
-------
JobsRepository persists Job records under data/{email.slug}/jobs/ with
key {id}.json. Path requires authenticated user (PrivateRepository).
Used by JobMutation, JobUpdateMutation, JobDetailsQuery, JobListQuery
(via index), StartTask, and ReportTask. NAME is "jobs"; MODEL is Job.
Only the owning user can access their jobs.

Examples:
>>> repo = JobsRepository(user=request.user)
>>> repo.save(job)
>>> job = repo.get(job_id)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from models import Job
from models import Model
from repositories.private import PrivateRepository


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
