"""
Interval type: list of exactly two Decimal (start, end) with start <= end. serialize/unserialize, contains, intersects, size. Measurable.

Title
-----
Interval (1D Range)

Context
-------
Interval is a 1D range [start, end] with start <= end. It implements
Measurable (size = end - start), Spatial (contains, intersects), and
Serializable. contains(Decimal or Interval) and intersects(Interval)
support inclusive bounds. Used by Box for x and y extent and in
intersection logic. Constructor and __setitem__ enforce start <= end.

Examples:
>>> i = Interval([Decimal("0"), Decimal("10")])
>>> i.contains(Decimal("5"))
>>> i.intersects(Interval([Decimal("5"), Decimal("15")]))
"""

from __future__ import annotations

from decimal import Decimal
from decimal import InvalidOperation
from typing import Any

from exceptions import ValidationError
from interfaces import Serializable
from interfaces.measurable import Measurable
from interfaces.spatial import Spatial


class Interval(list, Measurable, Spatial, Serializable[list[Any]]):
    """
    An interval as a list of exactly two Decimal values (start, end) with start <= end.

    Example:
    >>> i = Interval([Decimal("0"), Decimal("10")])
    >>> i.contains(Decimal("5"))
    True
    """

    def __init__(self, value: list[Decimal]) -> None:
        if not isinstance(value, list) or len(value) != 2:
            raise ValidationError("Interval requires a list of exactly 2 Decimal")
        start: Decimal = value[0]
        end: Decimal = value[1]
        if not isinstance(start, Decimal) or not isinstance(end, Decimal):
            raise ValidationError("Interval requires a list of exactly 2 Decimal")
        if start > end:
            raise ValidationError(f"Interval start must be <= end, got start={start} end={end}")
        super().__init__([start, end])

    def __setitem__(self, index: int, value: Any) -> None:
        if not isinstance(value, Decimal):
            raise ValidationError("Interval values must be Decimal")
        if index == 0:
            if value > self[1]:
                raise ValidationError(f"Interval start must be <= end, got start={value} end={self[1]}")
        elif index == 1:
            if self[0] > value:
                raise ValidationError(f"Interval start must be <= end, got start={self[0]} end={value}")
        else:
            raise IndexError("Interval index out of range")
        super().__setitem__(index, value)

    @property
    def start(self) -> Decimal:
        return self[0]

    @property
    def end(self) -> Decimal:
        return self[1]

    def __getitem__(self, index: int) -> Decimal:
        if index == 0:
            return super().__getitem__(0)
        if index == 1:
            return super().__getitem__(1)
        raise IndexError("Interval index out of range")

    @property
    def size(self) -> Decimal:
        return self[1] - self[0]

    def contains(self, obj: Decimal | Interval, inclusive: bool = True) -> bool:
        if isinstance(obj, Decimal):
            if inclusive:
                return self[0] <= obj <= self[1]
            return self[0] < obj < self[1]
        if isinstance(obj, Interval):
            if inclusive:
                return self[0] <= obj[0] and obj[1] <= self[1]
            return self[0] < obj[0] and obj[1] < self[1]
        raise ValidationError(f"Interval.contains expects Decimal or Interval, got {type(obj).__name__}")

    def intersects(self, obj: Interval, inclusive: bool = True) -> bool:
        if not isinstance(obj, Interval):
            raise ValidationError(f"Interval.intersects expects Interval, got {type(obj).__name__}")
        if inclusive:
            return self[0] <= obj[1] and obj[0] <= self[1]
        return self[0] < obj[1] and obj[0] < self[1]

    def serialize(self) -> list[str]:
        return [str(self[0]), str(self[1])]

    @classmethod
    def unserialize(cls, data: list[Any]) -> Interval:
        if not isinstance(data, (list, tuple)) or len(data) < 2:
            raise ValidationError("Interval.unserialize expects a list of at least 2 values")
        try:
            a: Decimal = data[0] if isinstance(data[0], Decimal) else Decimal(str(data[0]))
            b: Decimal = data[1] if isinstance(data[1], Decimal) else Decimal(str(data[1]))
        except (InvalidOperation, TypeError, ValueError):
            raise ValidationError("Interval.unserialize values must be valid numbers")
        return cls([a, b])
