from __future__ import annotations

import math
from decimal import Decimal
from functools import cached_property

from colorama import Fore

from box import Bounded, Box
from element import Element, Element1D, ElementSequence
from exceptions import (SegmentInvalidPointsError,
                        SegmentSequenceInvalidItemsError,
                        SequencePointNotFoundError)
from model import Hash
from path import Path
from point import Point, PointSequence


class Segment(Bounded, Element1D):
    def __init__(self, *, start: Point, end: Point) -> None:
        if not isinstance(start, Point):
            raise SegmentInvalidPointsError(
                f"start must be a Point, got {type(start).__name__}"
            )
        if not isinstance(end, Point):
            raise SegmentInvalidPointsError(
                f"end must be a Point, got {type(end).__name__}"
            )
        self.start = start
        self.end = end

    def __hash__(self) -> Hash:
        low: Point = min(self[0], self[1])
        high: Point = max(self[0], self[1])
        return Hash(f"segment:{low.__hash__()}:{high.__hash__()}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Segment):
            return False
        return (self[0] == other[0] and self[1] == other[1]) or (
            self[0] == other[1] and self[1] == other[0]
        )

    def __invert__(self) -> Segment:
        return Segment(start=self[1], end=self[0])

    def __getitem__(self, index: int) -> Point:
        if index == 0:
            return self.start
        elif index == 1:
            return self.end
        raise IndexError("Segment index out of range")

    def __repr__(self) -> str:
        return (
            f"{Fore.GREEN}({Fore.RESET}{self.start!r}{Fore.MAGENTA}--{Fore.RESET}"
            f"{self.end!r}{Fore.GREEN}){Fore.RESET}"
        )

    @property
    def size(self) -> Decimal:
        dx = self[1][0] - self[0][0]
        dy = self[1][1] - self[0][1]
        return (dx * dx + dy * dy).sqrt()

    @property
    def midpoint(self) -> Point:
        return Point(
            x=(self[0][0] + self[1][0]) / 2,
            y=(self[0][1] + self[1][1]) / 2,
        )

    @property
    def angle(self) -> Decimal:
        dx = float(self[1][0] - self[0][0])
        dy = float(self[1][1] - self[0][1])
        return Decimal(math.atan2(dy, dx))

    def contains(self, obj: Element, inclusive: bool = True) -> bool:
        if isinstance(obj, Point):
            return all(
                (
                    Path(start=self[0], center=self[1], end=obj).is_collinear(),
                    self.box.contains(obj, inclusive=inclusive),
                )
            )
        if isinstance(obj, Segment):
            return self.contains(obj[0], inclusive=inclusive) and self.contains(
                obj[1], inclusive=inclusive
            )
        raise NotImplementedError(f"Segment.contains not implemented for {type(obj)}")

    @cached_property
    def box(self) -> Box:
        min_x = min(self[0][0], self[1][0])
        max_x = max(self[0][0], self[1][0])
        min_y = min(self[0][1], self[1][1])
        max_y = max(self[0][1], self[1][1])
        return Box(
            bottom_left=Point(x=min_x, y=min_y),
            top_left=Point(x=min_x, y=max_y),
            bottom_right=Point(x=max_x, y=min_y),
            top_right=Point(x=max_x, y=max_y),
        )

    def connects(self, other: Segment) -> bool:
        return any(
            (
                self[0] == other[0],
                self[0] == other[1],
                self[1] == other[0],
                self[1] == other[1],
            )
        )

    def intersects(self, other: Segment, inclusive: bool = True) -> bool:
        if any(
            [
                self.box.x[1] < other.box.x[0],
                other.box.x[1] < self.box.x[0],
                self.box.y[1] < other.box.y[0],
                other.box.y[1] < self.box.y[0],
            ]
        ):
            return False
        path1: Path = Path(start=self[0], center=self[1], end=other[0])
        path2: Path = Path(start=self[0], center=self[1], end=other[1])
        path3: Path = Path(start=other[0], center=other[1], end=self[0])
        path4: Path = Path(start=other[0], center=other[1], end=self[1])
        if all(
            [
                all(
                    [
                        not path1.is_collinear(),
                        not path2.is_collinear(),
                        not path3.is_collinear(),
                        not path4.is_collinear(),
                    ]
                ),
                path1.orientation != path2.orientation,
                path3.orientation != path4.orientation,
            ]
        ):
            return True
        if any(
            [
                path1.is_collinear() and self.contains(other[0], inclusive=inclusive),
                path2.is_collinear() and self.contains(other[1], inclusive=inclusive),
                path3.is_collinear() and other.contains(self[0], inclusive=inclusive),
                path4.is_collinear() and other.contains(self[1], inclusive=inclusive),
            ]
        ):
            return True
        return False


class SegmentSequence(ElementSequence[Segment]):
    def __init__(self, items: list[Segment]) -> None:
        if not isinstance(items, list):
            raise SegmentSequenceInvalidItemsError(
                f"items must be a list, got {type(items).__name__}"
            )
        for i, segment in enumerate(items):
            if not isinstance(segment, Segment):
                raise SegmentSequenceInvalidItemsError(
                    f"items[{i}] must be a Segment, got {type(segment).__name__}"
                )
        self.items = SegmentSequence.clean(list(items))

    def __repr__(self) -> str:
        return (
            f"{Fore.BLUE}[{Fore.RESET}"
            f"{f'{Fore.BLUE} -> {Fore.RESET}'.join(repr(segment) for segment in self.items)}"
            f"{Fore.BLUE}]{Fore.RESET}"
        )

    @cached_property
    def points(self) -> PointSequence:
        return PointSequence([self.items[i][0] for i in range(len(self.items))])

    def is_ccw(self) -> bool:
        return self.points.is_ccw()

    def is_cw(self) -> bool:
        return self.points.is_cw()

    def is_convex(self) -> bool:
        return self.points.is_convex()

    def __lshift__(self, other: int | Segment | Point) -> SegmentSequence:
        n: int = len(self.items)
        if n == 0:
            return SegmentSequence(items=[])
        if isinstance(other, int):
            i = other % n
            return SegmentSequence(items=self.items[i:] + self.items[:i])
        if isinstance(other, Segment):
            for i, segment in enumerate(self.items):
                if segment == other:
                    return SegmentSequence(items=self.items[i:] + self.items[:i])
            raise ValueError(f"Segment {other!r} not in sequence")
        try:
            shifted = self.points << other
        except SequencePointNotFoundError as error:
            raise SequencePointNotFoundError(
                f"Point {other!r} not in segment sequence"
            ) from error
        return shifted.edges

    def __rshift__(self, other: int | Segment | Point) -> SegmentSequence:
        n: int = len(self.items)
        if n == 0:
            return SegmentSequence(items=[])
        if isinstance(other, int):
            i = other % n
            return SegmentSequence(items=self.items[i + 1 :] + self.items[: i + 1])
        if isinstance(other, Segment):
            for i, segment in enumerate(self.items):
                if segment == other:
                    return SegmentSequence(
                        items=self.items[i + 1 :] + self.items[: i + 1]
                    )
            raise ValueError(f"Segment {other!r} not in sequence")
        try:
            shifted = self.points >> other
        except SequencePointNotFoundError as error:
            raise SequencePointNotFoundError(
                f"Point {other!r} not in segment sequence"
            ) from error
        return shifted.edges

    def __hash__(self) -> Hash:
        if not self.items:
            return Hash("segment_sequence:empty")
        return Hash(f"segment_sequence:{self.points.__hash__()}")
