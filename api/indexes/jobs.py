"""
Per-user index for jobs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import ClassVar

from repositories.jobs import JobsRepository

from indexes.base import PrivateIndex


@dataclass
class JobsPrivateIndex(PrivateIndex[Any]):
    """
    Per-user index for jobs.
    """

    REPOSITORY: ClassVar[type] = JobsRepository
    NAME: ClassVar[str] = "jobs"
