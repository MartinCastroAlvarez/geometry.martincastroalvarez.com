from __future__ import annotations

from typing import Any

from exceptions import GuardInvalidPositionError
from model import Hash
from model import Model
from point import Point
from serializable import Serializable


class Guard(Model, Serializable):
    def serialize(self) -> dict[str, Any]:
        return {"id": int(self.id), "position": self.position.serialize()}

    def __init__(self, *, position: Point) -> None:
        super().__init__()
        self.position = position
        self.validate()
        self.id = Hash(f"guard:{self.position.__hash__()}")

    def validate(self) -> None:
        if not isinstance(self.position, Point):
            raise GuardInvalidPositionError(f"position must be a Point, got {type(self.position).__name__}")

    def __repr__(self) -> str:
        return f"Guard {self.id} {self.position}"


class VertexGuard(Guard):
    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> VertexGuard:
        if "position" not in data:
            raise GuardInvalidPositionError("VertexGuard.unserialize missing key 'position'")
        return cls(position=Point.unserialize(data["position"]))

    @property
    def vertex(self) -> Point:
        return self.position
