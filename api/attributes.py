"""
API value types and geometry re-exports.

Title
-----
Attributes Module (Value Types and Geometry)

Context
-------
This module defines validated value types used across the API: Timestamp,
Countdown, Identifier, Email, Url, Title, Path, Origin, Limit, Offset,
Slug, Signature, ReceiptHandle. Each enforces format and raises
ValidationError (or a specific exception) on invalid input. Geometry types
(Box, ConvexComponent, Ear, Walk, Point, Polygon, Segment, Interval,
Orientation) are re-exported via __getattr__ from the geometry package to
avoid circular imports. Data structures (Sequence, Table) live in structs/.
Use these types in request/response validation and in domain models.

Examples:
>>> from attributes import Timestamp, Email, Identifier, Path, Limit
>>> ts = Timestamp.now()
>>> email = Email("user@example.com")
>>> path = Path("/v1/galleries/abc")
>>> from attributes import Polygon, Point
"""

from __future__ import annotations

import hashlib
import re
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Any
from urllib.parse import ParseResult
from urllib.parse import urlparse

from exceptions import PathMissingResourceIdError
from exceptions import ValidationError
from settings import DEFAULT_ORIGIN
from settings import DEFAULT_TITLE_MAX_LENGTH
from settings import MAX_LIMIT
from slugify import slugify


class Path(str):
    """
    API path string. Stored without leading slashes. version = first segment, resource = second, id = third (raises if missing).

    For example, to parse path segments:
    >>> p = Path("/v1/galleries/abc")
    >>> p.version, p.resource, p.id
    ('v1', 'galleries', 'abc')
    """

    def __new__(cls, value: Any) -> Path:
        if value is None:
            value = ""
        raw = str(value).strip().lstrip("/")
        return super().__new__(cls, raw)

    @property
    def parts(self) -> list[str]:
        return [s for s in self.split("/") if s]

    @property
    def version(self) -> str:
        segs = self.parts
        return segs[0] if len(segs) >= 1 else ""

    @property
    def resource(self) -> str:
        segs = self.parts
        return segs[1] if len(segs) >= 2 else ""

    @property
    def id(self) -> str:
        segs = self.parts
        if len(segs) < 3:
            raise PathMissingResourceIdError("Path must include resource id (e.g. v1/galleries/:id)")
        return segs[2]


class Timestamp(str):
    """
    ISO 8601 timestamp string (e.g. for created_at, updated_at).

    Constructor accepts: None (uses now()), Timestamp, str, date, or datetime.
    Invalid input raises ValidationError.

    For example, to get current time and parse from string:
    >>> ts = Timestamp.now()
    >>> ts = Timestamp("2024-01-01T12:00:00.000000Z")
    >>> ts.to_datetime().year
    2024
    """

    ISO_FORMAT: str = "%Y-%m-%dT%H:%M:%S.%fZ"

    def __new__(
        cls,
        value: Any = None,
    ) -> Timestamp:
        if value is None:
            return cls.now()
        if isinstance(value, Timestamp):
            return super().__new__(cls, str(value))
        if isinstance(value, date) and not isinstance(value, datetime):
            return cls.from_date(value)
        if isinstance(value, datetime):
            return cls.from_datetime(value)
        if isinstance(value, str):
            return cls.from_iso(value)
        raise ValidationError(f"Timestamp must be None, Timestamp, str, date, or datetime, got {type(value).__name__}")

    @classmethod
    def now(cls) -> Timestamp:
        """
        Return a Timestamp for the current UTC time in ISO format.

        For example, to set created_at:
        >>> ts = Timestamp.now()
        >>> "T" in str(ts)
        True
        """
        return cls(datetime.now(timezone.utc))

    @classmethod
    def from_iso(cls, value: Any) -> Timestamp:
        """
        Parse an ISO timestamp string and return a Timestamp.
        Raises ValidationError if value is not a string or is invalid.

        For example, to parse from API data:
        >>> ts = Timestamp.from_iso("2024-01-01T12:00:00.000000Z")
        >>> str(ts)[:10]
        '2024-01-01'
        """
        if not isinstance(value, str):
            raise ValidationError(f"Timestamp.from_iso expects a string, got {type(value).__name__}")
        raw: str = value.strip()
        if not raw:
            return super().__new__(cls, datetime.now(timezone.utc).strftime(cls.ISO_FORMAT))
        try:
            if "T" in raw:
                dt: datetime = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            return super().__new__(cls, dt.strftime(cls.ISO_FORMAT))
        except ValueError as err:
            raise ValidationError(f"Invalid ISO timestamp: {raw!r}") from err

    @classmethod
    def from_date(cls, value: date) -> Timestamp:
        """Build a Timestamp from a date (midnight)."""
        combined: datetime = datetime.combine(value, datetime.min.time())
        return super().__new__(cls, combined.strftime(cls.ISO_FORMAT))

    @classmethod
    def from_datetime(cls, value: datetime) -> Timestamp:
        """Build a Timestamp from a datetime."""
        return super().__new__(cls, value.strftime(cls.ISO_FORMAT))

    def to_datetime(self) -> datetime:
        """
        Convert this Timestamp to a datetime.
        Raises ValidationError if the string is empty or invalid.
        """
        raw: str = str(self).strip()
        if not raw:
            raise ValidationError("Timestamp is empty")
        try:
            if "T" in raw:
                return datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError as err:
            raise ValidationError(f"Invalid date/time: {raw!r}") from err

    def to_date(self) -> date:
        """Convert this Timestamp to a date."""
        return self.to_datetime().date()

    def to_iso(self) -> str:
        """Return the ISO 8601 string representation of this timestamp."""
        return str(self)


class Countdown(int):
    """
    Integer sort key for "newest first": (FAR_FUTURE - value) in total_seconds, multiplied by 10**PRECISION.

    Constructor accepts only an integer > 0 (or Countdown). Use from_datetime, from_date, from_timestamp for other types.

    For example, to build a countdown from a timestamp for indexing:
    >>> cd = Countdown.from_timestamp(Timestamp.now())
    >>> cd > 0
    True
    """

    FAR_FUTURE: datetime = datetime(9999, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc)
    PRECISION: int = 8

    def __new__(cls, value: Any) -> Countdown:
        if isinstance(value, Countdown):
            return super().__new__(cls, int(value))
        if not isinstance(value, int):
            raise ValidationError("Countdown must be an integer")
        if value <= 0:
            raise ValidationError("Countdown must be greater than 0")
        return super().__new__(cls, value)

    @classmethod
    def from_datetime(cls, value: datetime) -> Countdown:
        """Build Countdown from a datetime. Naive datetimes are treated as UTC."""
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
        delta: timedelta = cls.FAR_FUTURE - value
        multiplier: int = 10**cls.PRECISION
        result: int = int(delta.total_seconds() * multiplier)
        return cls(result)

    @classmethod
    def from_date(cls, value: date) -> Countdown:
        """Build Countdown from a date (midnight)."""
        dt: datetime = datetime.combine(value, datetime.min.time())
        return cls.from_datetime(dt)

    @classmethod
    def from_timestamp(cls, value: Timestamp) -> Countdown:
        """Build Countdown from a Timestamp."""
        dt: datetime = value.to_datetime()
        return cls.from_datetime(dt)


class Signature(int):
    """
    An integer derived from hashing a value (for use as __hash__).
    Constructor accepts Any; if not None, the value is cast to str in a deterministic way
    (str(value)) before hashing, so callers need not cast. None raises; empty string becomes ":empty:".

    For example, to build a stable id from boundary+obstacles:
    >>> sig = Signature(f"{hash(boundary)}_{hash(obstacles)}")
    >>> Identifier(sig)
    Identifier('...')
    """

    LENGTH: int = 32

    def __new__(cls, value: Any) -> Signature:
        if value is None:
            raise ValidationError("Signature value must not be None")
        if not isinstance(value, str):
            value = str(value)
        if len(value) == 0:
            value = ":empty:"
        raw: bytes = value.encode()
        hashed: bytes = hashlib.sha256(raw).digest()[: cls.LENGTH]
        int_value: int = int.from_bytes(hashed, "big")
        return super().__new__(cls, int_value)

    def __hash__(self) -> Signature:
        return self


class Slug(str):
    """
    A string slug: validated (not None, non-empty string) and normalized to
    lowercase with non-alphanumeric replaced by a single dash, stripped.

    For example, to normalize a string for URLs:
    >>> slug = Slug("My Gallery Title")
    >>> str(slug)
    'my-gallery-title'
    """

    def __new__(cls, value: Any) -> Slug:
        if value is None:
            raise ValidationError("Slug is required")
        if not isinstance(value, str):
            raise ValidationError("Slug must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Slug must be a non-empty string")
        normalized: str = slugify(raw, separator="-", lowercase=True) or "x"
        return super().__new__(cls, normalized)


class Email(str):
    """
    A string that must be a valid email format. Raises ValidationError (400) if invalid.

    For example, to validate and get URL-safe slug:
    >>> email = Email("user@example.com")
    >>> email.slug
    Slug('user-example-com-...')
    """

    PATTERN = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __new__(cls, value: Any = None) -> Email:
        if value is None:
            raise ValidationError("Email is required")
        if not isinstance(value, str):
            raise ValidationError("Email must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Email must be a non-empty string")
        if not cls.PATTERN.match(raw):
            raise ValidationError("Email must be a valid email address")
        return super().__new__(cls, raw)

    @property
    def slug(self) -> Slug:
        """
        URL-safe identifier for this email: Slug(email) + '-' + Signature(email).
        Using the signature avoids collisions when two emails slugify to the same string.

        For example, to get storage path for user data:
        >>> user.email.slug
        Slug('alice-example-com-12345678')
        """
        return Slug(f"{Slug(self)}-{Signature(self)}")


class Identifier(str):
    """
    A string identifier that allows only letters, digits, underscore (_), and dash (-).
    Accepts str or int (int is cast to str). Raises ValidationError for empty or invalid characters.

    For example, to parse from path or body:
    >>> id = Identifier("gallery-123")
    >>> str(id)
    'gallery-123'
    """

    PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

    def __new__(cls, value: Any = None) -> Identifier:
        if value is None:
            raise ValidationError("Identifier is required")
        if isinstance(value, int):
            raw = str(value).strip()
        elif isinstance(value, str):
            raw = value.strip()
        else:
            raise ValidationError("Identifier argument must be a string or int")
        if not raw:
            raise ValidationError("Identifier must be a non-empty string")
        if not cls.PATTERN.match(raw):
            raise ValidationError("Identifier may only contain letters, digits, underscore (_), and dash (-)")
        return super().__new__(cls, raw)


class Limit(int):
    """
    A positive integer limit for pagination, at least MIN and at most MAX.
    Inherits from int; use in search/query limit and bucket limit.

    For example, to cap list size:
    >>> limit = Limit(20)
    >>> limit
    20
    """

    MIN: int = 1
    MAX: int = MAX_LIMIT

    def __new__(cls, value: Any = None) -> Limit:
        if value is None:
            from settings import DEFAULT_LIMIT

            value = DEFAULT_LIMIT
        try:
            raw: int = int(value)
        except (TypeError, ValueError):
            raise ValidationError("Limit must be an integer")
        if raw < cls.MIN:
            raise ValidationError(f"Limit must be at least {cls.MIN}")
        if raw > cls.MAX:
            raise ValidationError(f"Limit must be at most {cls.MAX}")
        return super().__new__(cls, raw)


class Offset(str):
    """
    A non-empty string for pagination (e.g. next_token).
    Does not accept None; use Offset | None where the token is optional.
    Raises ValidationError for None, non-string, or empty value.

    For example, to pass next_token from previous response:
    >>> token = Offset(response.get("next_token"))
    >>> results = repo.search(next_token=token)
    """

    def __new__(cls, value: Any) -> Offset:
        if value is None:
            raise ValidationError("Offset is required")
        if not isinstance(value, str):
            raise ValidationError("Offset must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Offset must be a non-empty string")
        return super().__new__(cls, raw)


class Origin(str):
    """
    CORS origin string. Normalizes according to allowed patterns:
    - Empty or invalid -> "*"
    - https://<any>.martincastroalvarez.com (e.g. https://geometry.martincastroalvarez.com) -> as-is
    - http://localhost or http://localhost:* (e.g. http://localhost:5174) -> as-is
    - Other -> DEFAULT_ORIGIN from settings

    For example, to normalize request origin:
    >>> Origin("https://geometry.martincastroalvarez.com")
    Origin('https://geometry.martincastroalvarez.com')
    >>> Origin("https://app.martincastroalvarez.com")
    Origin('https://app.martincastroalvarez.com')
    >>> Origin("http://localhost:5174")
    Origin('http://localhost:5174')
    >>> Origin("")
    Origin('*')
    """

    def __new__(cls, value: Any = None) -> Origin:
        if value is None:
            return super().__new__(cls, "*")
        raw = str(value).strip().rstrip("/") if value else ""
        if not raw:
            return super().__new__(cls, "*")
        if raw.startswith("https://") and (raw.endswith(".martincastroalvarez.com") or raw == "https://martincastroalvarez.com"):
            return super().__new__(cls, raw)
        if raw == "http://localhost" or raw.startswith("http://localhost:"):
            return super().__new__(cls, raw)
        return super().__new__(cls, DEFAULT_ORIGIN)


class ReceiptHandle(str):
    """
    A non-empty string, e.g. SQS message receipt handle.
    Raises ValidationError for None, non-string, or empty value.

    For example, to wrap SQS ReceiptHandle:
    >>> handle = ReceiptHandle(sqs_message["ReceiptHandle"])
    >>> queue.delete(handle)
    """

    def __new__(cls, value: Any = None) -> ReceiptHandle:
        if value is None:
            raise ValidationError("Receipt handle is required")
        if not isinstance(value, str):
            raise ValidationError("Receipt handle must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Receipt handle must be a non-empty string")
        return super().__new__(cls, raw)


class Title(str):
    """
    A string title with length validation.

    For example, to validate gallery title:
    >>> title = Title("My Gallery", max_length=200)
    >>> str(title)
    'My Gallery'
    """

    def __new__(
        cls,
        value: Any,
        *,
        min_length: int = 1,
        max_length: int = DEFAULT_TITLE_MAX_LENGTH,
    ) -> Title:
        if value is None:
            raise ValidationError("Title is required")
        if not isinstance(value, str):
            raise ValidationError("Title must be a string")
        raw: str = value.strip()
        if min_length > 0 and len(raw) < min_length:
            raise ValidationError(f"Title must be at least {min_length} character(s)")
        if len(raw) > max_length:
            raise ValidationError(f"Title must be at most {max_length} character(s)")
        return super().__new__(cls, raw)


class Url(str):
    """
    A string that must be a valid URL (with scheme and netloc). Raises ValidationError (400) if invalid.

    For example, to validate avatar URL:
    >>> url = Url("https://example.com/avatar.png")
    >>> str(url).startswith("https")
    True
    """

    def __new__(cls, value: Any = None) -> Url:
        if value is None:
            raise ValidationError("Url is required")
        if not isinstance(value, str):
            raise ValidationError("Url must be a string")
        raw: str = value.strip()
        if not raw:
            raise ValidationError("Url must be a non-empty string")
        parsed: ParseResult = urlparse(raw)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("Url must be a valid URL with scheme and host")
        if parsed.scheme not in ("http", "https", "ftp", "mailto"):
            raise ValidationError("Url scheme must be one of: http, https, ftp, mailto")
        return super().__new__(cls, raw)


_GEOMETRY_NAMES = frozenset(
    {
        "Box",
        "ConvexComponent",
        "Ear",
        "Interval",
        "Orientation",
        "Point",
        "Polygon",
        "Segment",
        "Visibility",
        "Walk",
    }
)


def __getattr__(name: str):
    if name in _GEOMETRY_NAMES:
        import geometry

        return getattr(geometry, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
