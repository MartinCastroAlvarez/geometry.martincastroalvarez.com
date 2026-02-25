"""
Shared helpers for mutations.
"""

from __future__ import annotations

from attributes import Email
from attributes import Identifier
from attributes import Signature


def gallery_id_from_job_and_user(job_id: Identifier, user_email: Email) -> Identifier:
    """Stable gallery id: Identifier of the Signature of the concatenation of job_id and user_email."""
    return Identifier(Signature(f"{job_id}_{user_email}"))
