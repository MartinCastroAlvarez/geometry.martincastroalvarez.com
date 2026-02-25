"""
ArtGallery model: boundary, obstacles, ears, convex_components, guards, visibility; owner_email, owner_job_id.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from attributes import Email
from attributes import Identifier
from attributes import Point
from attributes import Timestamp
from geometry import ConvexComponent
from geometry import Ear
from geometry import Polygon

from models.base import Model


@dataclass
class ArtGallery(Model):
    """
    Art gallery with boundary, obstacles, and computed attributes (ears, convex_components, guards, visibility).
    owner_email and owner_job_id link to the job and user that created it.

    Example:
    >>> data = gallery.serialize()
    >>> gallery = ArtGallery.unserialize(data)
    """

    id: Identifier
    boundary: Polygon
    obstacles: list[Polygon] = field(default_factory=list)
    owner_email: Email
    owner_job_id: Identifier
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    ears: list[Ear] = field(default_factory=list)
    convex_components: list[ConvexComponent] = field(default_factory=list)
    guards: list[Point] = field(default_factory=list)
    visibility: dict[Point, list[Point]] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"ArtGallery(id={self.id})"

    def __repr__(self) -> str:
        return f"ArtGallery(id={self.id!r}, owner_email={self.owner_email!r}, owner_job_id={self.owner_job_id!r})"

    @classmethod
    def unserialize(cls, data: dict[str, Any]) -> ArtGallery:
        boundary: Polygon = Polygon.unserialize(data.get("boundary") or [])

        obstacles: list[Polygon] = [
            Polygon.unserialize(obs) for obs in (data.get("obstacles") or []) if isinstance(obs, list)
        ]

        ears: list[Ear] = [
            Ear(list(Polygon.unserialize(seq))) for seq in (data.get("ears") or []) if isinstance(seq, list)
        ]

        convex_components: list[ConvexComponent] = [
            ConvexComponent(list(Polygon.unserialize(comp)))
            for comp in (data.get("convex_components") or []) if isinstance(comp, list)
        ]

        guards: list[Point] = [Point.unserialize(p) for p in data.get("guards") or []]

        visibility: dict[Point, list[Point]] = {}
        for k, points in (data.get("visibility") or {}).items():
            key_pt = Point.unserialize(k)
            visibility[key_pt] = [Point.unserialize(p) for p in points] if isinstance(points, list) else []

        return cls(
            id=Identifier(data.get("id")),
            boundary=boundary,
            obstacles=obstacles,
            owner_email=Email(data.get("owner_email")),
            owner_job_id=Identifier(data.get("owner_job_id")),
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
            ears=ears,
            convex_components=convex_components,
            guards=guards,
            visibility=visibility,
        )

    def serialize(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "boundary": self.boundary.serialize(),
            "obstacles": [poly.serialize() for poly in self.obstacles],
            "owner_email": str(self.owner_email),
            "owner_job_id": str(self.owner_job_id),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "ears": [seq.serialize() for seq in self.ears],
            "convex_components": [seq.serialize() for seq in self.convex_components],
            "guards": [json.loads(p.serialize()) for p in self.guards],
            "visibility": {k.serialize(): [json.loads(p.serialize()) for p in v] for k, v in self.visibility.items()},
        }
