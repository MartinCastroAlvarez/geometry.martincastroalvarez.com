from __future__ import annotations

import hashlib
from decimal import Decimal
from functools import cached_property
from typing import TYPE_CHECKING, Any

from colorama import Fore

from element import Element, ElementSequence
from exceptions import PointInvalidCoordinatesError

if TYPE_CHECKING:
    from segment import Segment, SegmentSequence

from exceptions import (CentroidEmptySequenceError,
                        ComponentsNoSharedEdgeError,
                        ConvexComponentSequenceSubtractionEmptyError,
                        ConvexComponentSequenceSubtractionError,
                        SequenceInvalidPointsError, SequencePointNotFoundError,
                        SequenceShiftValidationError)


class Point(Element):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and isinstance(args[0], dict):
            kwargs = args[0]
            args = ()
        if kwargs and "x" in kwargs and "y" in kwargs:
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
        if len(args) == 1 and isinstance(args[0], Point):
            self.x = args[0].x
            self.y = args[0].y
            return
        if len(args) == 2:
            self.x = (
                args[0]
                if isinstance(args[0], Decimal)
                else Decimal(str(float(args[0])))
            )
            self.y = (
                args[1]
                if isinstance(args[1], Decimal)
                else Decimal(str(float(args[1])))
            )
            return
        if len(args) == 1 and isinstance(args[0], (tuple, list)) and len(args[0]) == 2:
            a, b = args[0][0], args[0][1]
            self.x = a if isinstance(a, Decimal) else Decimal(str(float(a)))
            self.y = b if isinstance(b, Decimal) else Decimal(str(float(b)))
            return
        if kwargs and "x" in kwargs:
            val = kwargs["x"]
            if isinstance(val, Point):
                self.x = val.x
                self.y = val.y
                return
            if isinstance(val, (tuple, list)) and len(val) == 2:
                self.x = (
                    val[0]
                    if isinstance(val[0], Decimal)
                    else Decimal(str(float(val[0])))
                )
                self.y = (
                    val[1]
                    if isinstance(val[1], Decimal)
                    else Decimal(str(float(val[1])))
                )
                return
        raise PointInvalidCoordinatesError(
            "Point expects kwargs x and y, one dict, one Point, two coords, or [x,y]"
        )

    def to(self, other: Point) -> Segment:
        from segment import Segment

        return Segment(start=self, end=other)

    def __hash__(self) -> int:
        data: bytes = f"{self[0]},{self[1]}".encode()
        return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")

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


class PointSequence(ElementSequence[Point]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if len(args) == 1 and isinstance(args[0], dict):
            kwargs = args[0]
            args = ()
        if kwargs and ("items" in kwargs or "points" in kwargs):
            raw = kwargs.get("points", kwargs.get("items"))
            if isinstance(raw, PointSequence):
                raw = list(raw.items)
            else:
                raw = list(raw) if raw is not None else []
            coerced: list[Point] = []
            for index, point in enumerate(raw):
                if isinstance(point, Point):
                    coerced.append(point)
                else:
                    try:
                        coerced.append(
                            Point(point)
                            if not isinstance(point, dict)
                            else Point(**point)
                        )
                    except Exception as e:
                        raise SequenceInvalidPointsError(
                            f"PointSequence item at index {index} could not be coerced to Point: {point!r}"
                        ) from e
            self.items = coerced
            return
        if len(args) == 1 and isinstance(args[0], PointSequence):
            self.items = list(args[0].items)
            return
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            raw = list(args[0])
            coerced = []
            for index, point in enumerate(raw):
                if isinstance(point, Point):
                    coerced.append(point)
                else:
                    try:
                        coerced.append(
                            Point(point)
                            if not isinstance(point, dict)
                            else Point(**point)
                        )
                    except Exception as e:
                        raise SequenceInvalidPointsError(
                            f"PointSequence item at index {index} could not be coerced to Point: {point!r}"
                        ) from e
            self.items = coerced
            return
        self.items = []

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
        if isinstance(other, int):
            i = other % len(self.items)
        else:
            try:
                i = self.index(other)
            except ValueError as e:
                raise SequencePointNotFoundError(
                    f"Point {other!r} not in sequence"
                ) from e
        n = len(self.items)
        if n == 0:
            return PointSequence()
        new_items = self.items[i:] + self.items[:i]
        shifted = PointSequence(new_items)
        if self != shifted:
            raise SequenceShiftValidationError(
                "Shift result is not equal to original sequence (circular)"
            )
        return shifted

    def __rshift__(self, other: int | Point) -> PointSequence:
        if isinstance(other, int):
            i = other % len(self.items)
        else:
            try:
                i = self.index(other)
            except ValueError as e:
                raise SequencePointNotFoundError(
                    f"Point {other!r} not in sequence"
                ) from e
        n = len(self.items)
        if n == 0:
            return PointSequence()
        new_items = self.items[i + 1 :] + self.items[: i + 1]
        shifted = PointSequence(new_items)
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
