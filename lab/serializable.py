from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any


class Serializable(ABC):
    @abstractmethod
    def serialize(self) -> dict[str, Any]:
        raise NotImplementedError()

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> Any:
        raise NotImplementedError(f"{cls.__name__}.unserialize is not implemented")
