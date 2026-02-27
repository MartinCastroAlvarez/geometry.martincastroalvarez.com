"""
ISO 8601 timestamp type for created_at, updated_at.

Title
-----
Timestamp Attribute

Context
-------
Timestamp is an ISO 8601 string type used for created_at and updated_at
on models. The constructor accepts None (then uses now()), a Timestamp,
a str (parsed via from_iso), or date/datetime. Invalid input raises
ValidationError. from_iso, from_date, and from_datetime are class
methods for explicit construction. to_datetime() and to_date() convert
back for arithmetic. The canonical format includes microseconds and Z.
Used by Model, Job, ArtGallery, User and by indexes (Countdown).

Examples:
>>> ts = Timestamp.now()
>>> ts = Timestamp("2025-02-22T12:00:00Z")
>>> ts = Timestamp(None)  # same as now()
>>> dt = ts.to_datetime()
"""

from __future__ import annotations

from datetime import date
from datetime import datetime
from typing import Any

from exceptions import ValidationError


class Timestamp(str):
    """
    ISO 8601 timestamp string (e.g. for created_at, updated_at).

    Constructor accepts: None (uses now()), Timestamp, str, date, or datetime.
    Invalid input raises ValidationError.

    Example:
    >>> ts = Timestamp.now()
    >>> ts2 = Timestamp("2025-02-22T12:00:00Z")
    >>> ts3 = Timestamp(None)  # same as Timestamp.now()
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
        """Return a Timestamp for the current UTC time in ISO format."""
        return cls(datetime.utcnow())

    @classmethod
    def from_iso(cls, value: Any) -> Timestamp:
        """
        Parse an ISO timestamp string and return a Timestamp.
        Raises ValidationError if value is not a string or is invalid.
        """
        if not isinstance(value, str):
            raise ValidationError(f"Timestamp.from_iso expects a string, got {type(value).__name__}")
        raw: str = value.strip()
        if not raw:
            return super().__new__(cls, datetime.utcnow().strftime(cls.ISO_FORMAT))
        try:
            if "T" in raw:
                dt: datetime = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S")
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
            return datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError as err:
            raise ValidationError(f"Invalid date/time: {raw!r}") from err

    def to_date(self) -> date:
        """Convert this Timestamp to a date."""
        return self.to_datetime().date()
