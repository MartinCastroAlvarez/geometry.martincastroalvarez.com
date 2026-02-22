from __future__ import annotations

from abc import ABC, abstractmethod

from exceptions import GuardInvalidPositionError
from model import Model
from point import Point


class Guard(Model, ABC):
    def __init__(self, *, position: Point) -> None:
        super().__init__()
        if not isinstance(position, Point):
            raise GuardInvalidPositionError(
                f"position must be a Point, got {type(position).__name__}"
            )
        self.position = position

    @property
    @abstractmethod
    def vertex(self) -> Point: ...  # noqa

    def __repr__(self) -> str:
        return f"Guard {self.id} {self.position}"


class VertexGuard(Guard):
    @property
    def vertex(self) -> Point:
        return self.position
