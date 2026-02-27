"""
Domain models for the art gallery API.

Title
-----
Models Package

Context
-------
This package defines the domain models: Model (base), ArtGallery, Job, User.
All implement Serializable[dict] for S3 persistence and JSON API transport.
Model has id, created_at, updated_at; subclasses add fields and implement
serialize/unserialize. ArtGallery holds boundary, obstacles, ears, convex
components, guards, visibility, owner_email, owner_job_id. Job holds
status, stage, stdin, stdout, meta, stderr, parent/children. User holds
email, name, avatar_url and is used for auth and private repos. Used by
repositories, indexes, mutations, and queries.

Examples:
    from models import ArtGallery, Job, User
    gallery = ArtGallery.unserialize(data)
    job = Job.unserialize(data)
    user = request.user
"""

from models.base import Model
from models.gallery import ArtGallery
from models.job import Job
from models.user import User

__all__ = [
    "ArtGallery",
    "Job",
    "Model",
    "User",
]
