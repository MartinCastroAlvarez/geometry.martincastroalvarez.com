"""
Path type: API request path (str), normalized (no leading slashes). version, resource, id.

Title
-----
Path Attribute

Context
-------
Path represents the API request path after normalizing (strip, remove
leading slashes). The path is split into parts by "/"; version is the
first segment (e.g. "v1"), resource the second (e.g. "galleries", "jobs"),
and id the third when present. The id property raises PathMissingResourceIdError
if there are fewer than three segments; it is used by the handler to
extract the resource id for detail routes. Path supports startswith for
route matching in the handler. Stored and compared as a string.

Examples:
>>> Path("/v1/galleries")   # version=v1, resource=galleries
>>> Path("v1/jobs/abc")    # version=v1, resource=jobs, id=abc
>>> path.id                # raises if path has no third segment
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
