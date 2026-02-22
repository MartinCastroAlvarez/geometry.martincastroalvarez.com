from __future__ import annotations

import hashlib
import math
from decimal import Decimal
from functools import cached_property

from colorama import Fore

from box import Bounded, Box
from element import Element, Element1D, ElementSequence
from exceptions import (SegmentInvalidPointsError,
                        SegmentSequenceInvalidItemsError)
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

    def __hash__(self) -> int:
        low: Point = min(self[0], self[1])
        high: Point = max(self[0], self[1])
        data: bytes = f"{low[0]},{low[1]},{high[0]},{high[1]}".encode()
        return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")

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

    def overlaps(self, obj: Element, inclusive: bool = True) -> bool:
        raise NotImplementedError(f"Segment.overlaps not implemented for {type(obj)}")

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
        if not self.box.overlaps(other.box, inclusive=inclusive):
            return False
        self_start: Point = self[0]
        self_end: Point = self[1]
        other_start: Point = other[0]
        other_end: Point = other[1]
        path1: Path = Path(start=self_start, center=self_end, end=other_start)
        path2: Path = Path(start=self_start, center=self_end, end=other_end)
        path3: Path = Path(start=other_start, center=other_end, end=self_start)
        path4: Path = Path(start=other_start, center=other_end, end=self_end)
        return any(
            [
                all(
                    [
                        any(
                            [
                                path1.is_cw() and path2.is_ccw(),
                                path1.is_ccw() and path2.is_cw(),
                            ]
                        ),
                        any(
                            [
                                path3.is_cw() and path4.is_ccw(),
                                path3.is_ccw() and path4.is_cw(),
                            ]
                        ),
                    ]
                ),
                path1.is_collinear()
                and self.contains(other_start, inclusive=inclusive),
                path2.is_collinear() and self.contains(other_end, inclusive=inclusive),
                path3.is_collinear()
                and other.contains(self_start, inclusive=inclusive),
                path4.is_collinear() and other.contains(self_end, inclusive=inclusive),
            ]
        )


class SegmentSequence(ElementSequence[Segment]):
    def __init__(self, items: list[Segment]) -> None:
        if not isinstance(items, list):
            raise SegmentSequenceInvalidItemsError(
                f"items must be a list, got {type(items).__name__}"
            )
        for i, seg in enumerate(items):
            if not isinstance(seg, Segment):
                raise SegmentSequenceInvalidItemsError(
                    f"items[{i}] must be a Segment, got {type(seg).__name__}"
                )
        self.items = list(items)

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
