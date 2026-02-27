"""
ArtGallery model: boundary, obstacles, ears, convex_components, guards, visibility; owner_email, owner_job_id, owner_image_url.

Title
-----
ArtGallery Model

Context
-------
ArtGallery is the main gallery entity: boundary (Polygon), obstacles
(Table[Polygon]), and computed pipeline outputs (ears, convex_components,
guards, visibility). owner_email, owner_job_id and owner_image_url (Url | None)
link to the creating user and job. title is a Title. Serialized shape includes
all fields for S3 and API. Used by ArtGalleryRepository, ArtGalleryPublicIndex,
ArtGalleryPublishMutation, ArtGalleryHideMutation, and list/details queries.

Examples:
>>> data = gallery.serialize()
>>> gallery = ArtGallery.unserialize(data)
>>> repo.save(gallery)
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any

from attributes import Email
from attributes import Identifier
from attributes import Point
from attributes import Timestamp
from attributes import Title
from attributes import Url
from geometry import ConvexComponent
from geometry import Ear
from geometry import Polygon
from models.base import Model
from models.base import ModelDict
from structs import Sequence
from structs import Table


class ArtGalleryDict(ModelDict):
    """Serialized form of ArtGallery (serialize/unserialize)."""

    boundary: list[Any]
    obstacles: dict[str, Any]
    owner_email: str
    owner_job_id: str
    owner_image_url: str | None
    title: str
    ears: dict[str, Any]
    convex_components: dict[str, Any]
    guards: dict[str, Any]
    visibility: dict[str, Any]


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
    owner_email: Email
    owner_job_id: Identifier
    title: Title
    owner_image_url: Url | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    obstacles: Table[Polygon] = field(default_factory=Table)
    ears: Table[Ear] = field(default_factory=Table)
    convex_components: Table[ConvexComponent] = field(default_factory=Table)
    guards: Table[Point] = field(default_factory=Table)
    visibility: Table[Sequence[Point]] = field(default_factory=Table)

    def __str__(self) -> str:
        return f"ArtGallery(id={self.id})"

    def __repr__(self) -> str:
        return f"ArtGallery(id={self.id!r}, owner_email={self.owner_email!r}, owner_job_id={self.owner_job_id!r})"

    @classmethod
    def unserialize(cls, data: Any) -> ArtGallery:
        raw_owner_image_url = data.get("owner_image_url")
        owner_image_url = Url(raw_owner_image_url) if raw_owner_image_url else None
        return cls(
            id=Identifier(data.get("id")),
            boundary=Polygon.unserialize(data.get("boundary") or []),
            obstacles=Table.unserialize([Polygon.unserialize(v) for v in data.get("obstacles", {}).values()]),
            owner_email=Email(data.get("owner_email")),
            owner_job_id=Identifier(data.get("owner_job_id")),
            owner_image_url=owner_image_url,
            title=Title(data.get("title", "Untitled Art Gallery")),
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
            ears=Table.unserialize([Ear.unserialize(v) for v in data.get("ears", {}).values()]),
            convex_components=Table.unserialize([ConvexComponent.unserialize(v) for v in data.get("convex_components", {}).values()]),
            guards=Table.unserialize([Point.unserialize(v) for v in data.get("guards", {}).values()]),
            visibility=Table.unserialize([Sequence([Point.unserialize(p) for p in points]) for points in data.get("visibility", {}).values()]),
        )

    def serialize(self) -> ArtGalleryDict:
        return {
            "id": str(self.id),
            "boundary": self.boundary.serialize(),
            "obstacles": self.obstacles.serialize(),
            "owner_email": str(self.owner_email),
            "owner_job_id": str(self.owner_job_id),
            "owner_image_url": str(self.owner_image_url) if self.owner_image_url is not None else None,
            "title": str(self.title),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "ears": self.ears.serialize(),
            "convex_components": self.convex_components.serialize(),
            "guards": self.guards.serialize(),
            "visibility": self.visibility.serialize(),
        }
