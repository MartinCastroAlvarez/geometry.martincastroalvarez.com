from __future__ import annotations

from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any

from colorama import Fore

from element import Element, ElementSequence
from exceptions import (PointInvalidCoordinatesError,
                        SerializedInvalidDictError,
                        SerializedInvalidValueError, SerializedMissingKeyError)
from model import Hash
from serializable import Serializable

if TYPE_CHECKING:
    from segment import Segment, SegmentSequence

from exceptions import (CentroidEmptySequenceError,
                        ComponentsNoSharedEdgeError,
                        ConvexComponentSequenceSubtractionEmptyError,
                        ConvexComponentSequenceSubtractionError,
                        SequenceInvalidPointsError, SequencePointNotFoundError,
                        SequenceShiftValidationError)


def _coerce_to_points(raw: list[Any]) -> list[Point]:
    out: list[Point] = []
    for index, item in enumerate(raw):
        if isinstance(item, Point):
            out.append(item)
        else:
            try:
                out.append(Point(item) if not isinstance(item, dict) else Point(**item))
            except Exception as error:
                raise SequenceInvalidPointsError(
                    f"PointSequence item at index {index} could not be coerced to Point: {item!r}"
                ) from error
    return out


class Point(Element, Serializable):
    x: Decimal
    y: Decimal

    def serialize(self) -> dict[str, Any]:
        return {"x": self.x, "y": self.y}

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> Point:
        if not isinstance(data, dict):
            raise SerializedInvalidDictError(
                f"Point.unserialize expects a dict, got {type(data).__name__}"
            )
        if "x" not in data:
            raise SerializedMissingKeyError("Point.unserialize missing key 'x'")
        if "y" not in data:
            raise SerializedMissingKeyError("Point.unserialize missing key 'y'")
        try:
            x = (
                data["x"]
                if isinstance(data["x"], Decimal)
                else Decimal(str(float(data["x"])))
            )
            y = (
                data["y"]
                if isinstance(data["y"], Decimal)
                else Decimal(str(float(data["y"])))
            )
        except (TypeError, ValueError) as error:
            raise PointInvalidCoordinatesError(
                f"Point.unserialize invalid x/y: {error}"
            ) from error
        return cls(x=x, y=y)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and not kwargs:
            one = args[0]
            if isinstance(one, Point):
                self.x, self.y = one.x, one.y
                return
            parsed = self.__class__.unserialize(one)
            self.x, self.y = parsed.x, parsed.y
            return
        if "x" in kwargs and "y" in kwargs:
            self.x = (
                kwargs["x"]
                if isinstance(kwargs["x"], Decimal)
                else Decimal(str(float(kwargs["x"])))
            )
            self.y = (
                kwargs["y"]
                if isinstance(kwargs["y"], Decimal)
                else Decimal(str(float(kwargs["y"])))
            )
            return
        raise PointInvalidCoordinatesError(
            "Point expects (x=..., y=...) or a single Point/dict"
        )

    def to(self, other: Point) -> Segment:
        from segment import Segment

        return Segment(start=self, end=other)

    def __hash__(self) -> Hash:
        return Hash(f"point:{self[0]}:{self[1]}")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Point):
            return False
        return self[0] == other[0] and self[1] == other[1]

    def __lt__(self, other: Point) -> bool:
        if self[0] != other[0]:
            return self[0] < other[0]
        return self[1] < other[1]

    def __sub__(self, other: Point) -> Point:
        return Point(x=self[0] - other[0], y=self[1] - other[1])

    def __add__(self, other: Point) -> Point:
        return Point(x=self[0] + other[0], y=self[1] + other[1])

    def __len__(self) -> int:
        return 2

    def __getitem__(self, index: int) -> Decimal:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Point index out of range")

    def __repr__(self) -> str:
        return f"{Fore.CYAN}({int(self[0])}, {int(self[1])}){Fore.RESET}"


class PointSequence(ElementSequence[Point], Serializable):
    def serialize(self) -> dict[str, Any]:
        return {"points": [point.serialize() for point in self.items]}

    @classmethod
    def unserialize(cls, data: dict[str, Any] | list[Any]) -> PointSequence:
        if isinstance(data, dict):
            if "points" not in data:
                raise SerializedMissingKeyError(
                    "PointSequence.unserialize missing key 'points'"
                )
            raw = data["points"]
        elif isinstance(data, list):
            raw = data
        else:
            raise SerializedInvalidDictError(
                f"PointSequence.unserialize expects a dict or list, got {type(data).__name__}"
            )
        if not isinstance(raw, list):
            raise SerializedInvalidValueError(
                f"PointSequence.unserialize 'points' must be a list, got {type(raw).__name__}"
            )
        points: list[Point] = []
        for item in raw:
            if isinstance(item, Point):
                points.append(item)
            elif isinstance(item, dict):
                points.append(Point.unserialize(item))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                points.append(Point.unserialize({"x": item[0], "y": item[1]}))
            else:
                raise SerializedInvalidValueError(
                    f"PointSequence.unserialize point must be dict or [x,y], got {type(item).__name__}"
                )
        return cls(points=points)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and not kwargs:
            one = args[0]
            if isinstance(one, PointSequence):
                self.items = PointSequence.clean(list(one.items))
                return
            if isinstance(one, dict):
                try:
                    parsed = self.__class__.unserialize(one)
                    self.items = parsed.items
                    return
                except Exception:
                    pass
            if isinstance(one, (list, tuple)):
                self.items = PointSequence.clean(_coerce_to_points(list(one)))
                return
            raise SequenceInvalidPointsError(
                f"PointSequence expects a PointSequence, a dict, or a list; got {type(one).__name__}"
            )
        raw = kwargs.get("points", kwargs.get("items"))
        if raw is not None:
            sequence = list(raw.items) if isinstance(raw, PointSequence) else list(raw)
            self.items = PointSequence.clean(_coerce_to_points(sequence))
            return
        self.items = PointSequence.clean([])

    def __repr__(self) -> str:
        return (
            f"{Fore.BLUE}[{Fore.RESET}"
            f"{f'{Fore.BLUE} -> {Fore.RESET}'.join(repr(point) for point in self.items)}"
            f"{Fore.BLUE}]{Fore.RESET}"
        )

    @cached_property
    def signed_area(self) -> Decimal:
        from matrix import Matrix

        n: int = len(self.items)
        if n < 3:
            return Decimal("0")
        area2: Decimal = sum(
            (Matrix([self[i], self[i + 1]]).determinant for i in range(n)),
            start=Decimal("0"),
        )
        return area2 / Decimal("2")

    def is_ccw(self) -> bool:
        return len(self.items) >= 3 and self.signed_area > Decimal("0")

    def is_cw(self) -> bool:
        return len(self.items) >= 3 and self.signed_area < Decimal("0")

    def is_convex(self) -> bool:
        from path import Orientation, Path

        n: int = len(self.items)
        if n < 3:
            return False
        orientation: Orientation | None = None
        for i in range(n):
            path: Path = Path(start=self[i - 1], center=self[i], end=self[i + 1])
            if path.is_collinear():
                continue
            if orientation is None:
                orientation = path.orientation
            elif path.orientation != orientation:
                return False
        return orientation is not None

    @cached_property
    def leftmost(self) -> Point:
        return min(self.items, key=lambda point: (point[0], point[1]))

    @cached_property
    def rightmost(self) -> Point:
        return max(self.items, key=lambda point: (point[0], point[1]))

    @cached_property
    def bottommost(self) -> Point:
        return min(self.items, key=lambda point: (point[1], point[0]))

    @cached_property
    def topmost(self) -> Point:
        return max(self.items, key=lambda point: (point[1], point[0]))

    @cached_property
    def centroid(self) -> Point:
        if not self.items:
            raise CentroidEmptySequenceError(
                "Cannot compute centroid of an empty PointSequence."
            )
        sx: Decimal = Decimal("0")
        sy: Decimal = Decimal("0")
        for point in self.items:
            sx += point.x
            sy += point.y
        n: Decimal = Decimal(str(len(self.items)))
        return Point(x=sx / n, y=sy / n)

    @cached_property
    def edges(self) -> SegmentSequence:
        from segment import Segment, SegmentSequence

        n: int = len(self.items)
        return SegmentSequence(
            items=[Segment(start=self[i], end=self[i + 1]) for i in range(n)]
        )

    def __lshift__(self, other: int | Point) -> PointSequence:
        n = len(self.items)
        if n == 0:
            return PointSequence()
        if isinstance(other, int):
            i = other % n
        else:
            try:
                i = self.index(other)
            except ValueError as error:
                raise SequencePointNotFoundError(
                    f"Point {other!r} not in sequence"
                ) from error
        shifted = PointSequence(self.items[i:] + self.items[:i])
        if self != shifted:
            raise SequenceShiftValidationError(
                "Shift result is not equal to original sequence (circular)"
            )
        return shifted

    def __rshift__(self, other: int | Point) -> PointSequence:
        n = len(self.items)
        if n == 0:
            return PointSequence()
        if isinstance(other, int):
            i = other % n
        else:
            try:
                i = self.index(other)
            except ValueError as error:
                raise SequencePointNotFoundError(
                    f"Point {other!r} not in sequence"
                ) from error
        shifted = PointSequence(self.items[i + 1 :] + self.items[: i + 1])
        if self != shifted:
            raise SequenceShiftValidationError(
                "Shift result is not equal to original sequence (circular)"
            )
        return shifted

    def __add__(self, other: PointSequence) -> PointSequence:
        if self.items[0] == other.items[0]:
            return PointSequence(self.items + other.items[1:])
        if self.items[0] == other.items[-1]:
            return PointSequence(other.items + self.items[1:])
        if self.items[-1] == other.items[0]:
            return PointSequence(self.items + other.items[1:])
        if self.items[-1] == other.items[-1]:
            return PointSequence(self.items + other.items[-2::-1])
        return PointSequence(self.items + other.items)

    def __sub__(self, other: PointSequence) -> PointSequence:
        n: int = len(self.items)
        k: int = len(other.items)
        if n == 0 or k == 0:
            raise ConvexComponentSequenceSubtractionEmptyError(
                "Cannot subtract: sequence is empty"
            )
        for i in range(n):
            matches: bool = all(
                self.items[(i + j) % n] == other.items[j] for j in range(k)
            )
            if matches:
                if k == n:
                    return PointSequence()
                return PointSequence(
                    [self.items[((i + k) % n + j) % n] for j in range(n - k)]
                )
        raise ConvexComponentSequenceSubtractionError("Sequence not found in polygon")

    def __and__(self, other: PointSequence) -> PointSequence:
        left_edges: set = set(self.edges)
        right_edges: set = set(other.edges)
        shared_edges: set = left_edges & right_edges
        if not shared_edges:
            raise ComponentsNoSharedEdgeError(
                "Components do not share an edge or merge failed"
            )
        edge = shared_edges.pop()
        return PointSequence([edge[0], edge[1]])

    def __invert__(self) -> PointSequence:
        return PointSequence(list(reversed(self.items)))

    def __hash__(self) -> Hash:
        if not self.items:
            return Hash("point_sequence:empty")

        def canonical_key(seq: PointSequence) -> tuple[tuple[Decimal, Decimal], ...]:
            rotated = seq << seq.leftmost
            return tuple((point[0], point[1]) for point in rotated.items)

        forward_key = canonical_key(self)
        backward_key = canonical_key(~self)
        return Hash(f"point_sequence:{min(forward_key, backward_key)}")
