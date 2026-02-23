from __future__ import annotations

from decimal import Decimal
from typing import Any

from element import Element, Element1D
from exceptions import (IntervalInvalidError, SerializedInvalidDictError,
                        SerializedMissingKeyError)
from serializable import Serializable


class Interval(Element1D, Serializable):
    def serialize(self) -> dict[str, Any]:
        return {"start": self.start, "end": self.end}

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> Interval:
        if not isinstance(data, dict):
            raise SerializedInvalidDictError(
                f"Interval.unserialize expects a dict, got {type(data).__name__}"
            )
        if "start" not in data:
            raise SerializedMissingKeyError("Interval.unserialize missing key 'start'")
        if "end" not in data:
            raise SerializedMissingKeyError("Interval.unserialize missing key 'end'")
        try:
            start = (
                data["start"]
                if isinstance(data["start"], Decimal)
                else Decimal(str(float(data["start"])))
            )
            end = (
                data["end"]
                if isinstance(data["end"], Decimal)
                else Decimal(str(float(data["end"])))
            )
        except (TypeError, ValueError) as error:
            raise IntervalInvalidError(
                f"Interval.unserialize invalid start/end: {error}"
            ) from error
        return cls(start=start, end=end)

    def __init__(self, *, start: Decimal, end: Decimal) -> None:
        self.start = start
        self.end = end
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.start, Decimal):
            raise IntervalInvalidError(
                f"start must be a Decimal, got {type(self.start).__name__}"
            )
        if not isinstance(self.end, Decimal):
            raise IntervalInvalidError(
                f"end must be a Decimal, got {type(self.end).__name__}"
            )
        if self.end < self.start:
            raise IntervalInvalidError(
                f"Interval end ({self.end}) must be >= start ({self.start})"
            )

    def contains(self, obj: Decimal | Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Decimal):
            if inclusive:
                return self[0] <= obj <= self[1]
            else:
                return self[0] < obj < self[1]

        if isinstance(obj, Interval):
            if inclusive:
                return self[0] <= obj[0] and obj[1] <= self[1]
            else:
                return self[0] < obj[0] and obj[1] < self[1]

        raise NotImplementedError(f"Interval.contains not implemented for {type(obj)}")

    def intersects(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Interval):
            if inclusive:
                return self[0] <= obj[1] and obj[0] <= self[1]
            return self[0] < obj[1] and obj[0] < self[1]
        raise NotImplementedError(
            f"Interval.intersects not implemented for {type(obj)}"
        )

    def __getitem__(self, index: int) -> Decimal:
        if index == 0:
            return self.start
        elif index == 1:
            return self.end
        raise IndexError("Interval index out of range")

    @property
    def size(self) -> Decimal:
        return self[1] - self[0]
