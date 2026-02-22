from __future__ import annotations

from decimal import Decimal

from element import Element, Element1D
from exceptions import IntervalInvalidError


class Interval(Element1D):
    def __init__(self, *, start: Decimal, end: Decimal) -> None:
        if not isinstance(start, Decimal):
            raise IntervalInvalidError(
                f"start must be a Decimal, got {type(start).__name__}"
            )
        if not isinstance(end, Decimal):
            raise IntervalInvalidError(
                f"end must be a Decimal, got {type(end).__name__}"
            )
        self.start = start
        self.end = end
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

    def overlaps(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Interval):
            if inclusive:
                return self[0] <= obj[1] and obj[0] <= self[1]
            return self[0] < obj[1] and obj[0] < self[1]
        return False

    def __getitem__(self, index: int) -> Decimal:
        if index == 0:
            return self.start
        elif index == 1:
            return self.end
        raise IndexError("Interval index out of range")

    @property
    def size(self) -> Decimal:
        return self[1] - self[0]
