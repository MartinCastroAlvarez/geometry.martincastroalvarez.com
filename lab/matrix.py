from __future__ import annotations

from decimal import Decimal

from exceptions import (MatrixDimensionError, MatrixEmptyError,
                        MatrixInvalidPointsError, MatrixNotSquareError)
from point import Point, PointSequence


class Matrix:
    def __init__(self, points: list[Point]) -> None:
        if not isinstance(points, list):
            raise MatrixInvalidPointsError(
                f"points must be a list, got {type(points).__name__}"
            )
        for i, p in enumerate(points):
            if not isinstance(p, Point):
                raise MatrixInvalidPointsError(
                    f"points[{i}] must be a Point, got {type(p).__name__}"
                )
        self.points = PointSequence(points)
        if len(self.points) == 0:
            raise MatrixEmptyError("Matrix cannot be empty")
        if any(len(point) != len(self.points[0]) for point in self.points):
            raise MatrixDimensionError("All points must have the same length")

    @property
    def dimensions(self) -> tuple[int, int]:
        return (len(self.points), len(self.points[0]))

    def is_squared(self) -> bool:
        return self.dimensions[0] == self.dimensions[1]

    @property
    def determinant(self) -> Decimal:
        if not self.is_squared():
            raise MatrixNotSquareError(
                "Matrix must be squared to calculate determinant"
            )

        if self.dimensions == (2, 2):
            return (
                self.points[0][0] * self.points[1][1]
                - self.points[0][1] * self.points[1][0]
            )

        raise NotImplementedError("Determinant only implemented for 2x2 matrices")
