"""
Serialized (dict) shapes for API and S3 transport.

Title
-----
Serializers Module

Context
-------
TypedDicts that describe the JSON-serialized form of domain models.
Serialized is the parent type used as Serializable[T] in models; ModelDict
is the base shape; UserDict, JobDict, ArtGalleryDict extend it.
"""

from __future__ import annotations

from typing import Any
from typing import TypedDict


class Serialized(TypedDict, total=False):
    """Parent shape for any serialized model (used as Serializable[T] in models)."""

    pass


class ModelDict(Serialized):
    """Base shape for serialized Model instances."""

    id: str
    created_at: str
    updated_at: str


class UserDict(ModelDict):
    """Serialized form of User (serialize/unserialize)."""

    email: str
    name: str
    avatar_url: str | None


class JobDict(ModelDict):
    """Serialized form of Job (serialize/unserialize)."""

    parent_id: str | None
    children_ids: list[str]
    status: str
    step_name: str
    stdin: dict[str, Any]
    stdout: dict[str, Any]
    meta: dict[str, Any]
    stderr: dict[str, Any]
    duration: int


class JobStateDict(ModelDict):
    """Serialized form of JobState (serialize/unserialize)."""

    data: dict[str, Any]


class ArtGalleryDict(ModelDict):
    """Serialized form of ArtGallery (serialize/unserialize)."""

    boundary: list[Any]
    obstacles: dict[str, Any]
    owner_job_id: str
    title: str
    ears: dict[str, Any]
    convex_components: dict[str, Any]
    adjacency: dict[str, Any]
    guards: dict[str, Any]
    visibility: dict[str, Any]
    exclusivity: dict[str, Any]
    stitched: list[Any]
    stitches: list[Any]
    duration: int
    coverage: list[Any]
