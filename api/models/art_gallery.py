"""
ArtGallery model: boundary, obstacles, ears, convex_components, guards, visibility; owner_email, owner_job_id.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from attributes import Email
from attributes import Identifier
from attributes import Point
from attributes import Polygon
from attributes import Timestamp

from models.base import Model


@dataclass
class ArtGallery(Model):
    """
    Art gallery with boundary, obstacles, and computed attributes (ears, convex_components, guards, visibility).
    owner_email and owner_job_id link to the job and user that created it.

    Example:
    >>> data = gallery.to_dict()
    >>> gallery = ArtGallery.from_dict(data)
    """

    id: Identifier
    boundary: list[tuple[str, str]]
    obstacles: list[list[tuple[str, str]]]
    owner_email: Email
    owner_job_id: Identifier
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    ears: list[Polygon[Point]] = field(default_factory=list)
    convex_components: list[Polygon[Point]] = field(default_factory=list)
    guards: list[Point] = field(default_factory=list)
    visibility: dict[Point, list[Point]] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"ArtGallery(id={self.id})"

    def __repr__(self) -> str:
        return f"ArtGallery(id={self.id!r}, owner_email={self.owner_email!r}, owner_job_id={self.owner_job_id!r})"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArtGallery:
        def coerce_boundary(v: Any) -> list[tuple[str, str]]:
            if not v:
                return []
            if isinstance(v, list) and v and isinstance(v[0], (list, tuple)) and len(v[0]) >= 2:
                return [tuple(str(x) for x in p[:2]) for p in v]
            return []

        def coerce_obstacles(v: Any) -> list[list[tuple[str, str]]]:
            if not v:
                return []
            out: list[list[tuple[str, str]]] = []
            for obs in v:
                if isinstance(obs, list):
                    out.append([tuple(str(x) for x in p[:2]) for p in obs if isinstance(p, (list, tuple)) and len(p) >= 2])
                else:
                    out.append([])
            return out

        def coerce_ears(v: Any) -> list[Polygon[Point]]:
            if not v or not isinstance(v, list):
                return []
            return [
                Polygon.from_list(seq, Point.from_list) if isinstance(seq, list) else Polygon([])
                for seq in v
            ]

        def coerce_convex(v: Any) -> list[Polygon[Point]]:
            if not v or not isinstance(v, list):
                return []
            return [
                Polygon.from_list(comp, Point.from_list) if isinstance(comp, list) else Polygon([])
                for comp in v
            ]

        def coerce_guards(v: Any) -> list[Point]:
            if not v or not isinstance(v, list):
                return []
            return [Point.from_list(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else Point(["0", "0"]) for p in v]

        def coerce_visibility(v: Any) -> dict[Point, list[Point]]:
            if not v or not isinstance(v, dict):
                return {}
            out: dict[Point, list[Point]] = {}
            for k, points in v.items():
                if isinstance(k, (list, tuple)) and len(k) >= 2:
                    key_pt = Point.from_list(k)
                else:
                    parts = str(k).split(",")
                    key_pt = Point.from_list(parts) if len(parts) >= 2 else Point(["0", "0"])
                if isinstance(points, list):
                    out[key_pt] = [
                        Point.from_list(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else Point(["0", "0"])
                        for p in points
                    ]
                else:
                    out[key_pt] = []
            return out

        return cls(
            id=Identifier(str(data.get("id", ""))),
            boundary=coerce_boundary(data.get("boundary")),
            obstacles=coerce_obstacles(data.get("obstacles")),
            owner_email=Email(str(data.get("owner_email", "") or "nobody@unknown.local")),
            owner_job_id=Identifier(str(data.get("owner_job_id", ""))),
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
            ears=coerce_ears(data.get("ears")),
            convex_components=coerce_convex(data.get("convex_components")),
            guards=coerce_guards(data.get("guards")),
            visibility=coerce_visibility(data.get("visibility")),
        )

    def to_dict(self) -> dict[str, Any]:
        def point_to_key(p: Point) -> str:
            return f"{p.x},{p.y}"

        return {
            "id": str(self.id),
            "boundary": list(self.boundary),
            "obstacles": [list(obs) for obs in self.obstacles],
            "owner_email": str(self.owner_email),
            "owner_job_id": str(self.owner_job_id),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "ears": [seq.to_list() for seq in self.ears],
            "convex_components": [seq.to_list() for seq in self.convex_components],
            "guards": [p.to_list() for p in self.guards],
            "visibility": {point_to_key(k): [p.to_list() for p in v] for k, v in self.visibility.items()},
        }
