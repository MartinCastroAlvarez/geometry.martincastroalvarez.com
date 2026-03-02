"""
Domain models for the art gallery API.

Title
-----
Models Module

Context
-------
This module defines the domain models: Model (base), ArtGallery, Job, User.
All implement Serializable[dict] for S3 persistence and JSON API transport.
Model has id, created_at, updated_at; subclasses add fields and implement
serialize/unserialize. ArtGallery holds boundary, obstacles, ears, convex
components, guards, visibility, stitched, owner_job_id. Job holds
status, step_name, stdin, stdout, meta, stderr, parent/children. User holds
email, name, avatar_url and is used for auth and private repos. Used by
repositories, indexes, mutations, and queries.

Examples:
>>> from models import ArtGallery, Job, User
>>> gallery = ArtGallery.unserialize(data)
>>> job = Job.unserialize(data)
>>> user = request.user
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from attributes import Email
from attributes import Identifier
from attributes import Signature
from attributes import Timestamp
from attributes import Title
from attributes import Url
from enums import Status
from enums import StepName
from exceptions import ValidationError
from geometry import ConvexComponent
from geometry import Ear
from geometry import Point
from geometry import Polygon
from geometry import Segment
from interfaces import Serializable
from serializers import ArtGalleryDict
from serializers import JobDict
from serializers import Serialized
from serializers import UserDict
from settings import ANONYMOUS_AVATAR_URL
from settings import ANONYMOUS_EMAIL as SETTINGS_ANONYMOUS_EMAIL
from settings import ANONYMOUS_NAME
from settings import DEFAULT_TITLE_MAX_LENGTH
from settings import TEST_AVATAR_URL
from settings import TEST_EMAIL
from settings import TEST_NAME
from settings import UNTITLED_ART_GALLERY_NAME
from structs import Bag
from structs import Table


class Model(Serializable[Serialized]):
    """
    Abstract base for all persisted models. id (Identifier), created_at, updated_at are attributes.

    For example, to unserialize a model from API/S3 data:
    >>> gallery = ArtGallery.unserialize(data)
    >>> gallery.id
    Identifier('...')
    """

    id: Identifier
    created_at: Timestamp
    updated_at: Timestamp

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError

    def __hash__(self) -> Signature:
        return Signature(self.id)

    @classmethod
    @abstractmethod
    def unserialize(cls, data: dict[str, Any]) -> Model:
        raise NotImplementedError

    @abstractmethod
    def serialize(self) -> Serialized:
        raise NotImplementedError


@dataclass
class User(Model):
    """
    User from JWT/auth. id is Identifier(Signature(email)); created_at/updated_at may be empty for auth-only user.
    If email is passed but not id, id is built from email. The constructor always validates id == Identifier(Signature(email)).

    For example, to create a user from JWT payload:
    >>> user = User.unserialize({"email": "u@example.com", "name": "User"})
    >>> user.is_authenticated()
    True
    """

    id: Identifier | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    email: Email = field(default_factory=lambda: Email(SETTINGS_ANONYMOUS_EMAIL))
    name: Title = field(default_factory=lambda: Title("", min_length=0, max_length=DEFAULT_TITLE_MAX_LENGTH))
    avatar_url: Url | None = None

    def __post_init__(self) -> None:
        if isinstance(self.name, str):
            self.name = Title(self.name, min_length=0, max_length=DEFAULT_TITLE_MAX_LENGTH)
        if isinstance(self.email, str):
            self.email = Email(self.email) if self.email.strip() else Email(SETTINGS_ANONYMOUS_EMAIL)
        if isinstance(self.avatar_url, str) and self.avatar_url.strip():
            self.avatar_url = Url(self.avatar_url)
        expected_id: Identifier = Identifier(Signature(self.email))
        if self.id is None:
            self.id = expected_id
        elif isinstance(self.id, str):
            self.id = Identifier(self.id) if self.id.strip() else expected_id
        if self.id != expected_id:
            raise ValidationError("User id must equal Identifier(Signature(email))")

    def __str__(self) -> str:
        return f"User(email={self.email})"

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"

    @classmethod
    def anonymous(cls) -> User:
        """
        Build and return the anonymous user (anonymous email, name, avatar from settings).

        For example, to get the anonymous user:
        >>> u = User.anonymous()
        >>> u.is_authenticated()
        False
        """
        return cls(
            name=ANONYMOUS_NAME,
            avatar_url=Url(ANONYMOUS_AVATAR_URL),
        )

    @classmethod
    def test(cls) -> User:
        """
        Build and return a user with test constants (TEST_EMAIL, TEST_NAME, TEST_AVATAR_URL).

        For example, to get a test user for unit tests:
        >>> u = User.test()
        >>> str(u.email)
        'test@test.com'
        """
        email = Email(TEST_EMAIL)
        return cls(
            id=Identifier(Signature(email)),
            email=email,
            name=TEST_NAME,
            avatar_url=Url(TEST_AVATAR_URL) if TEST_AVATAR_URL else None,
        )

    @classmethod
    def unserialize(cls, data: Any) -> User:
        """
        Build User from data. id is Identifier(Signature(email)); Email raises if empty or invalid.

        For example, to build a user from a dict:
        >>> user = User.unserialize({"email": "a@b.com", "name": "Alice"})
        >>> user.serialize()["email"]
        'a@b.com'
        """
        raw_email = str(data.get("email", "") or data.get("id", "")).strip()
        raw_avatar = data.get("avatar_url")
        email = Email(raw_email)
        return cls(
            id=Identifier(Signature(email)),
            email=email,
            name=Title(str(data.get("name", "")), min_length=0, max_length=DEFAULT_TITLE_MAX_LENGTH),
            avatar_url=Url(str(raw_avatar)) if raw_avatar else None,
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
        )

    def serialize(self) -> UserDict:
        return {
            "id": str(self.id),
            "email": str(self.email),
            "name": str(self.name),
            "avatar_url": str(self.avatar_url) if self.avatar_url is not None else None,
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }

    def is_authenticated(self) -> bool:
        """
        True if any attribute is not the anonymous sentinel (i.e. user is authenticated).

        For example, to check if the current user is logged in:
        >>> request.user.is_authenticated()
        True
        """
        anonymous_email = Email(SETTINGS_ANONYMOUS_EMAIL)
        if self.email != anonymous_email or self.name != ANONYMOUS_NAME:
            return True
        if self.avatar_url is not None and str(self.avatar_url) != ANONYMOUS_AVATAR_URL:
            return True
        return False


@dataclass
class Job(Model):
    """
    Job for async processing. parent_id, children_ids, status, step_name, stdin, stdout, meta, stderr.

    For example, to check job status:
    >>> job = Job.unserialize(data)
    >>> job.is_pending()
    True
    >>> job.serialize()["status"]
    'pending'
    """

    id: Identifier
    parent_id: Identifier | None = None
    children_ids: list[Identifier] = field(default_factory=list)
    status: Status = Status.PENDING
    step_name: StepName = StepName.ART_GALLERY
    stdin: dict[str, Any] = field(default_factory=dict)
    stdout: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    stderr: dict[str, Any] = field(default_factory=dict)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)

    def __str__(self) -> str:
        return f"Job(id={self.id}, status={self.status}, step_name={self.step_name})"

    def __repr__(self) -> str:
        return f"Job(id={self.id!r}, status={self.status!r}, step_name={self.step_name!r})"

    def is_pending(self) -> bool:
        """
        Return True if job status is PENDING.

        For example, to check if a job is still running:
        >>> job.is_pending()
        True
        """
        return self.status == Status.PENDING

    def is_failed(self) -> bool:
        """
        Return True if job status is FAILED.

        For example, to check if a job failed:
        >>> job.is_failed()
        False
        """
        return self.status == Status.FAILED

    def is_finished(self) -> bool:
        """
        Return True if job status is SUCCESS.

        For example, to check if a job completed successfully:
        >>> job.is_finished()
        True
        """
        return self.status == Status.SUCCESS

    @classmethod
    def unserialize(cls, data: Any) -> Job:
        """
        Build Job from dict. Parses status, step_name, children_ids, parent_id.

        For example, to load a job from S3 or API response:
        >>> job = Job.unserialize({"id": "abc", "status": "pending", "step_name": "art_gallery"})
        >>> job.id
        Identifier('abc')
        """
        raw_children = data.get("children_ids") or []
        children_ids: list[Identifier] = [Identifier(c) if not isinstance(c, Identifier) else c for c in raw_children]
        parent_raw = data.get("parent_id")
        parent_id: Identifier | None = Identifier(parent_raw) if parent_raw else None
        status_raw = data.get("status")
        status: Status = Status.parse(status_raw) if status_raw else Status.PENDING
        step_name_raw = data.get("step_name") or data.get("stage") or data.get("task")
        step_name: StepName = StepName.parse(step_name_raw) if step_name_raw else StepName.ART_GALLERY
        return cls(
            id=Identifier(data.get("id", "")),
            parent_id=parent_id,
            children_ids=children_ids,
            status=status,
            step_name=step_name,
            stdin=dict(data.get("stdin") or {}),
            stdout=dict(data.get("stdout") or {}),
            meta=dict(data.get("meta") or {}),
            stderr=dict(data.get("stderr") or {}),
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
        )

    def serialize(self) -> JobDict:
        return {
            "id": str(self.id),
            "parent_id": str(self.parent_id) if self.parent_id is not None else None,
            "children_ids": [str(c) for c in self.children_ids],
            "status": self.status.value,
            "step_name": str(self.step_name.slug),
            "stdin": dict(self.stdin),
            "stdout": dict(self.stdout),
            "meta": dict(self.meta),
            "stderr": dict(self.stderr),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
        }


@dataclass
class ArtGallery(Model):
    """
    Art gallery with boundary, obstacles, and computed attributes (ears, convex_components, guards, visibility, stitched, stitches).
    owner_job_id links to the job that created it. stitched is the polygon from the stitching step; stitches is the list
    of bridge edges added during stitching (optional).

    For example, to load a gallery from job stdout or repository:
    >>> gallery = ArtGallery.unserialize(data)
    >>> gallery.boundary.serialize()
    [...]
    >>> gallery.stitched  # Polygon or empty list when absent
    """

    id: Identifier
    boundary: Polygon
    owner_job_id: Identifier
    title: Title
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)
    obstacles: Table[Polygon] = field(default_factory=Table)
    ears: Table[Ear] = field(default_factory=Table)
    convex_components: Table[ConvexComponent] = field(default_factory=Table)
    adjacency: Table[Bag[ConvexComponent, Identifier]] = field(default_factory=Table)
    guards: Table[Point] = field(default_factory=Table)
    visibility: Table[Bag[Point, Point]] = field(default_factory=Table)
    stitched: Polygon = field(default_factory=lambda: Polygon([]))
    stitches: list[Segment] = field(default_factory=list)

    def __str__(self) -> str:
        return f"ArtGallery(id={self.id})"

    def __repr__(self) -> str:
        return f"ArtGallery(id={self.id!r}, owner_job_id={self.owner_job_id!r})"

    @classmethod
    def unserialize(cls, data: Any) -> ArtGallery:
        """
        Build ArtGallery from dict. Unserializes boundary, obstacles, ears, guards, visibility, stitched, stitches.
        stitched is optional; accepts key "stitched" or "stiteched"; defaults to empty polygon. stitches is optional list
        of segments (bridge edges from stitching step).

        For example, to build a gallery from publish response:
        >>> gallery = ArtGallery.unserialize({"id": "g1", "boundary": [...], "owner_job_id": "j1", ...})
        >>> gallery.boundary
        Polygon(...)
        >>> gallery = ArtGallery.unserialize({"id": "g1", "boundary": [...], "stitched": [[0,0],[1,0],[1,1]]})
        >>> len(gallery.stitched)
        3
        """
        boundary = data.get("boundary") or data.get("boundaries") or []
        obstacles_raw = data.get("obstacles") or data.get("holes") or []
        obstacles_list: list[Any] = list(obstacles_raw.values()) if isinstance(obstacles_raw, dict) else (obstacles_raw or [])
        ears_raw = data.get("ears") or []
        convex_components_raw = data.get("convex_components") or []
        guards_raw = data.get("guards") or []
        visibility_raw = data.get("visibility") or []
        stitched_raw = data.get("stitched") or data.get("stiteched") or []
        stitched = Polygon.unserialize(stitched_raw) if stitched_raw else Polygon([])
        stitches_raw = data.get("stitches") or []
        stitches = [Segment.unserialize(stitch) for stitch in stitches_raw] if stitches_raw else []

        ears_sequence = ears_raw.values() if isinstance(ears_raw, dict) else ears_raw
        ears = Table.unserialize([Ear.unserialize(ser) for ser in ears_sequence])

        cc_sequence = convex_components_raw.values() if isinstance(convex_components_raw, dict) else convex_components_raw
        convex_components = Table.unserialize([ConvexComponent.unserialize(cc) for cc in cc_sequence])

        def _adjacency_bag(component: ConvexComponent, hashes_list: Any) -> Bag[ConvexComponent, Identifier] | None:
            if not isinstance(hashes_list, (list, tuple)):
                return None
            bag: Bag[ConvexComponent, Identifier] = Bag(component)
            for h in hashes_list:
                bag += Identifier(int(h))
            return bag

        adjacency_raw = data.get("adjacency") or {}
        adjacency_bags = (
            [b for cc in convex_components for b in [_adjacency_bag(cc, adjacency_raw.get(str(cc.id), []))] if b is not None]
            if isinstance(adjacency_raw, dict)
            else []
        )
        adjacency_table: Table[Bag[ConvexComponent, Identifier]] = Table.unserialize(adjacency_bags)

        def _visibility_bag(guard: Point, pts_raw: Any) -> Bag[Point, Point] | None:
            if not isinstance(pts_raw, (list, tuple)):
                return None
            vis_bag: Bag[Point, Point] = Bag(guard)
            for p in pts_raw:
                vis_bag += Point.unserialize(p)
            return vis_bag

        if isinstance(guards_raw, dict):
            guards = Table.unserialize([Point.unserialize(serialized) for serialized in guards_raw.values()])
            visibility_bags = [
                b
                for k, guard_ser in guards_raw.items()
                for guard in [Point.unserialize(guard_ser)]
                for pts_raw in [(visibility_raw.get(k) or []) if isinstance(visibility_raw, dict) else []]
                for b in [_visibility_bag(guard, pts_raw)]
                if b is not None
            ]
            visibility_table: Table[Bag[Point, Point]] = Table.unserialize(visibility_bags)
        else:
            guards = Table.unserialize([Point.unserialize(guard) for guard in guards_raw])
            visibility_bags = (
                [b for guard, path in zip(list(guards.values()), visibility_raw) for b in [_visibility_bag(guard, path)] if b is not None]
                if isinstance(visibility_raw, list)
                else []
            )
            visibility_table = Table.unserialize(visibility_bags)

        id_raw = (data.get("id") or "").strip()
        owner_raw = (data.get("owner_job_id") or "").strip()
        return cls(
            id=Identifier(id_raw or "art-gallery"),
            boundary=Polygon.unserialize(boundary),
            obstacles=Table.unserialize([Polygon.unserialize(obstacle) for obstacle in obstacles_list]),
            owner_job_id=Identifier(owner_raw or "art-gallery"),
            title=Title(data.get("title", UNTITLED_ART_GALLERY_NAME)),
            created_at=Timestamp(data.get("created_at")),
            updated_at=Timestamp(data.get("updated_at")),
            ears=ears,
            convex_components=convex_components,
            adjacency=adjacency_table,
            guards=guards,
            visibility=visibility_table,
            stitched=stitched,
            stitches=stitches,
        )

    def serialize(self) -> ArtGalleryDict:
        return {
            "id": str(self.id),
            "boundary": self.boundary.serialize(),
            "obstacles": self.obstacles.serialize(),
            "owner_job_id": str(self.owner_job_id),
            "title": str(self.title),
            "created_at": str(self.created_at),
            "updated_at": str(self.updated_at),
            "ears": self.ears.serialize(),
            "convex_components": self.convex_components.serialize(),
            "adjacency": self.adjacency.serialize(),
            "guards": self.guards.serialize(),
            "visibility": {str(hash(bag.key)): [p.serialize() for p in bag.items] for bag in self.visibility},
            "stitched": self.stitched.serialize(),
            "stitches": [s.serialize() for s in self.stitches],
        }
