"""
Path type: API request path (str), normalized (no leading slashes). version, resource, id.
"""

from __future__ import annotations

from typing import Any

from exceptions import PathMissingResourceIdError


class Path(str):
    """
    API path string. Stored without leading slashes. version = first segment, resource = second, id = third (raises if missing).
    """

    def __new__(cls, value: Any) -> Path:
        if value is None:
            value = ""
        raw = str(value).strip().lstrip("/")
        return super().__new__(cls, raw)

    @property
    def parts(self) -> list[str]:
        return [s for s in self.split("/") if s]

    @property
    def version(self) -> str:
        segs = self.parts
        return segs[0] if len(segs) >= 1 else ""

    @property
    def resource(self) -> str:
        segs = self.parts
        return segs[1] if len(segs) >= 2 else ""

    @property
    def id(self) -> str:
        segs = self.parts
        if len(segs) < 3:
            raise PathMissingResourceIdError("Path must include resource id (e.g. v1/galleries/:id)")
        return segs[2]
