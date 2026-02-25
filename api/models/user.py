"""
User model: JWT/auth user (id=email). Used by private repositories and the private decorator.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from attributes import Email
from attributes import Identifier
from attributes import Timestamp
from attributes import Url

from models.base import Model


@dataclass
class User(Model):
    """
    User from JWT/auth. id is email; created_at/updated_at may be empty for auth-only user.

    For example, to check authentication before using a private repository:
    >>> if request.user.is_authenticated():
    ...     repo = JobRepository(user=request.user)

    To build a minimal user for the worker:
    >>> user = User(id=str(email), email=email)
    """

    id: Identifier = field(default_factory=lambda: Identifier("anonymous"))
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    email: Email | None = None
    name: str = ""
    avatar_url: Url | None = None

    def __post_init__(self) -> None:
        if isinstance(self.id, str):
            self.id = Identifier(self.id) if self.id.strip() else Identifier("anonymous")
        if isinstance(self.email, str):
            self.email = Email(self.email) if self.email.strip() else None
        if isinstance(self.avatar_url, str) and self.avatar_url.strip():
            self.avatar_url = Url(self.avatar_url)

    def __str__(self) -> str:
        return f"User(email={self.email})"

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        raw_email = str(data.get("email", "") or data.get("id", "")).strip()
        raw_avatar = data.get("avatar_url")
        return cls(
            id=Identifier(raw_email) if raw_email else Identifier("anonymous"),
            email=Email(raw_email) if raw_email else None,
            name=str(data.get("name", "")),
            avatar_url=Url(str(raw_avatar)) if raw_avatar else None,
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "email": str(self.email) if self.email is not None else "",
            "name": self.name,
            "avatar_url": str(self.avatar_url) if self.avatar_url is not None else None,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    def is_authenticated(self) -> bool:
        return self.email is not None
