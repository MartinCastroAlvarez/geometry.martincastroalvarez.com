"""
Point type: list of exactly two Decimal coordinates (x, y). Hashable, comparable, Serializable[str].
"""

from __future__ import annotations

import json
from decimal import Decimal
from decimal import InvalidOperation
from typing import TYPE_CHECKING
from typing import Any

from attributes.signature import Signature
from exceptions import ValidationError
from interfaces import Serializable

if TYPE_CHECKING:
    from geometry.segment import Segment


class Point(list, Serializable[str]):
    """
    A point as a list of exactly two Decimal values (x, y). Inherits from list.
    Implements serialize (-> str), unserialize (str | list); __hash__, __eq__, __lt__, __sub__, __len__, __getitem__.

    Example:
    >>> p = Point.unserialize(["1", "2"])
    >>> p.x, p.y
    (Decimal('1'), Decimal('2'))
    >>> p.to(Point.unserialize(["0", "0"]))
    """

    def __init__(
        self,
        value: list[Any] | tuple[Any, Any] | None = None,
    ) -> None:
        if value is None:
            raise ValidationError("Point requires a list or tuple of 2 values")
        if not isinstance(value, (list, tuple)):
            raise ValidationError(f"Point must be a list or tuple of 2 values, got {type(value).__name__}")
        if len(value) != 2:
            raise ValidationError(f"Point must have exactly 2 values, got {len(value)}")
        try:
            x: Decimal = value[0] if isinstance(value[0], Decimal) else Decimal(str(value[0]))
            y: Decimal = value[1] if isinstance(value[1], Decimal) else Decimal(str(value[1]))
        except (InvalidOperation, TypeError, ValueError):
            raise ValidationError("Point coordinates must be valid numbers")
        super().__init__([x, y])

    def __setitem__(self, index: int, value: Any) -> None:
        if index not in (0, 1):
            raise ValidationError(f"Point index must be 0 or 1, got {index}")
        if isinstance(value, Decimal):
            super().__setitem__(index, value)
            return
        try:
            super().__setitem__(index, Decimal(str(value)))
        except (InvalidOperation, TypeError, ValueError):
            raise ValidationError("Point value must be a Decimal or convertible to Decimal")

    @property
    def x(self) -> Decimal:
        return self[0]

    @property
    def y(self) -> Decimal:
        return self[1]

    def to(self, other: Point) -> Segment:
        from geometry.segment import Segment

        return Segment([self, other])

    def __hash__(self) -> Signature:
        return Signature(f"{self.x}:{self.y}")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __lt__(self, other: Point) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        if self.x != other.x:
            return self.x < other.x
        return self.y < other.y

    def __sub__(self, other: Point) -> Point:
        if not isinstance(other, Point):
            return NotImplemented
        return Point((self.x - other.x, self.y - other.y))

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, index: int) -> Decimal:
        if index == 0:
            return super().__getitem__(0)
        if index == 1:
            return super().__getitem__(1)
        raise IndexError("Point index out of range")

    def serialize(self) -> str:
        """Return JSON string of [x, y] for use as dict key or wire format."""
        return json.dumps([str(self.x), str(self.y)])

    @classmethod
    def unserialize(cls, data: str | list[Any]) -> Point:
        """
        Build Point from list of strings, list of decimals, or JSON str.
        Raises ValidationError on invalid JSON or data.
        """
        if isinstance(data, str):
            data = data.strip()
            if not data:
                raise ValidationError("Point.unserialize expects non-empty str or list")
            try:
                loaded: Any = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Point.unserialize invalid JSON: {e}") from e
            if not isinstance(loaded, (list, tuple)) or len(loaded) < 2:
                raise ValidationError("Point.unserialize JSON must be list of at least 2 values")
            return cls((loaded[0], loaded[1]))
        if isinstance(data, (list, tuple)) and len(data) >= 2:
            return cls((data[0], data[1]))
        raise ValidationError("Point.unserialize expects str (JSON), list of strings, or list of decimals")
