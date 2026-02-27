"""
Countdown sort key for "newest first" index ordering.

Title
-----
Countdown Attribute

Context
-------
Countdown is an integer sort key used to order index entries "newest first".
It is computed as (FAR_FUTURE - value) in total seconds, multiplied by
10**PRECISION, so that later timestamps yield smaller integers and sort
first when keys are listed in ascending order. The constructor accepts
only an integer > 0 (or Countdown). Use from_datetime, from_date, or
from_timestamp to build from time types. Used by ArtGalleryPublicIndex
and JobsPrivateIndex as index_id (e.g. Countdown.from_timestamp(gallery.created_at)).

Examples:
>>> key = Countdown.from_timestamp(Timestamp.now())
>>> key = Countdown.from_datetime(datetime.utcnow())
>>> index.save(Indexed(index_id=Identifier(key), real_id=record.id))
"""

from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any

from attributes.timestamp import Timestamp
from exceptions import ValidationError


class Countdown(int):
    """
    Integer sort key for "newest first": (FAR_FUTURE - value) in total_seconds, multiplied by 10**PRECISION.

    Constructor accepts only an integer > 0 (or Countdown). Use from_datetime, from_date, from_timestamp for other types.

    Example:
    >>> key = Countdown.from_timestamp(Timestamp.now())
    >>> key = Countdown.from_datetime(datetime.utcnow())
    """

    FAR_FUTURE: datetime = datetime(9999, 12, 31, 23, 59, 59, 999999)
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
        """Build Countdown from a datetime."""
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
