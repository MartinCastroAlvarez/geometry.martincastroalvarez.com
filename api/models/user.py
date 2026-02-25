"""
User model: JWT/auth user. id is Identifier(Signature(email)). Used by private repositories and the private decorator.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import ClassVar

from attributes import Email
from attributes import Identifier
from attributes import Signature
from attributes import Timestamp
from attributes import Url
from exceptions import ValidationError
from models.base import Model
from models.base import ModelDict


class UserDict(ModelDict):
    """Serialized form of User (serialize/unserialize)."""

    email: str
    name: str
    avatar_url: str | None


@dataclass
class User(Model):
    """
    User from JWT/auth. id is Identifier(Signature(email)); created_at/updated_at may be empty for auth-only user.
    If email is passed but not id, id is built from email. The constructor always validates id == Identifier(Signature(email)).

    For example, to check authentication before using a private repository:
    >>> if request.user.is_authenticated():
    ...     repo = JobRepository(user=request.user)

    To build a user: pass email (id is derived) or pass both id and email (validated).
    >>> user = User(email=email)
    >>> user = User(id=Identifier(Signature(email)), email=email)
    """

    ANONYMOUS_EMAIL: ClassVar[Email] = Email("nobody@unknown.local")
    ANONYMOUS_NAME: ClassVar[str] = "Anonymous"
    ANONYMOUS_AVATAR_URL: ClassVar[str] = "https://picsum.photos/200"
    ANONYMOUS_USER: ClassVar[User]
    TEST_EMAIL: ClassVar[str] = "test@test.com"
    TEST_NAME: ClassVar[str] = "test test"
    TEST_AVATAR_URL: ClassVar[str] = "https://picsum.photos/200"

    id: Identifier | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    email: Email = field(default_factory=lambda: User.ANONYMOUS_EMAIL)
    name: str = ""
    avatar_url: Url | None = None

    def __post_init__(self) -> None:
        if isinstance(self.email, str):
            self.email = Email(self.email) if self.email.strip() else User.ANONYMOUS_EMAIL
        if isinstance(self.avatar_url, str) and self.avatar_url.strip():
            self.avatar_url = Url(self.avatar_url)
        expected_id: Identifier = Identifier(Signature(self.email))
        if self.id is None:
            self.id = expected_id
        elif isinstance(self.id, str):
            self.id = Identifier(self.id) if self.id.strip() else expected_id
        if self.id != expected_id:
            raise ValidationError("User id must equal Identifier(Signature(email))")

    def __str__(self) -> str:
        return f"User(email={self.email})"

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

    @classmethod
    def anonymous(cls) -> User:
        """Return the shared anonymous user instance."""
        return cls.ANONYMOUS_USER

    @classmethod
    def test(cls) -> User:
        """Return a user instance with test constants (TEST_EMAIL, TEST_NAME, TEST_AVATAR_URL)."""
        email = Email(cls.TEST_EMAIL)
        return cls(
            id=Identifier(Signature(email)),
            email=email,
            name=cls.TEST_NAME,
            avatar_url=Url(cls.TEST_AVATAR_URL) if cls.TEST_AVATAR_URL else None,
        )

    @classmethod
    def unserialize(cls, data: Any) -> User:
        """Build User from data. id is Identifier(Signature(email)); Email raises if empty or invalid."""
        raw_email = str(data.get("email", "") or data.get("id", "")).strip()
        raw_avatar = data.get("avatar_url")
        email = Email(raw_email)
        return cls(
            id=Identifier(Signature(email)),
            email=email,
            name=str(data.get("name", "")),
            avatar_url=Url(str(raw_avatar)) if raw_avatar else None,
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
        )

    def serialize(self) -> UserDict:
        return {
            "id": str(self.id),
            "email": str(self.email),
            "name": self.name,
            "avatar_url": str(self.avatar_url) if self.avatar_url is not None else None,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    def is_authenticated(self) -> bool:
        """True if any attribute is not the anonymous sentinel (i.e. user is authenticated)."""
        if self is User.ANONYMOUS_USER:
            return False
        return any(
            [
                self.email != User.ANONYMOUS_EMAIL,
                self.name != User.ANONYMOUS_NAME,
                self.avatar_url is not User.ANONYMOUS_AVATAR_URL,
            ]
        )


User.ANONYMOUS_USER = User(
    name=User.ANONYMOUS_NAME,
    avatar_url=Url(User.ANONYMOUS_AVATAR_URL),
)
