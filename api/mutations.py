"""
Mutations for art galleries and jobs.

Title
-----
Mutations Module

Context
-------
This module exports write-side handlers: JobMutation (create job),
JobUpdateMutation (update job meta, sync title to gallery), ArtGalleryPublishMutation
(publish gallery from finished job).
All gallery and job mutations that require auth use PrivateControllerMixin
with Mutation and receive request.user. Mutations validate body, mutate state (repo, index,
queue), and return a response dict. Registered in api.api (ROUTES) by path and method.

Examples:
>>> from mutations import JobMutation, ArtGalleryPublishMutation
>>> handler = JobMutation(user=request.user)
>>> result = handler.handler(body)
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Any

from attributes import Countdown
from attributes import Email
from attributes import Identifier
from attributes import Signature
from attributes import Title
from controllers import Controller
from controllers import ControllerRequest
from controllers import ControllerResponse
from controllers import PrivateControllerMixin
from enums import Action
from enums import StepName
from exceptions import BoundaryRequiredError
from exceptions import JobNotFinishedToPublishError
from exceptions import JobStdoutMissingGeometryError
from exceptions import MetaKeysMustBeStringsError
from exceptions import MetaMustBeDictError
from exceptions import MetaRequiredError
from exceptions import MetaValuesMustBeStringsError
from exceptions import ObstaclesMustBeListError
from exceptions import PolygonValidationError
from exceptions import RecordNotFoundError
from exceptions import TitleMustBeStringError
from exceptions import UserNotAuthenticatedError
from geometry import Polygon
from indexes import ArtGalleryPublicIndex
from indexes import Indexed
from indexes import JobsPrivateIndex
from logger import get_logger
from messages import Message
from messages import Queue
from models import ArtGallery
from models import Job
from repositories import ArtGalleryRepository
from repositories import JobsRepository
from structs import Table
from validations import PolygonValidation

queue = Queue()
logger = get_logger(__name__)


class MutationRequest(ControllerRequest):
    """Base for mutation requests."""

    pass


class ArtGalleryPublishMutationRequest(MutationRequest):
    """Publish: job_id required; gallery data taken from job stdout."""

    job_id: Identifier


class JobMutationRequest(MutationRequest):
    """Create job: boundary and obstacles; id is hash (idempotent). Optional title (default: Untitled Gallery)."""

    boundary: Polygon
    obstacles: Table[Polygon]
    title: str


class JobUpdateMutationRequest(MutationRequest):
    """Update job: job_id from path; metadata only."""

    job_id: Identifier
    meta: dict[str, str]


class JobDeleteMutationRequest(MutationRequest):
    """Delete job: job_id from path. Recursively deletes children then the job."""

    job_id: Identifier


class MutationResponse(ControllerResponse):
    """Base for mutation outputs."""

    pass


class ArtGalleryPublishMutationResponse(MutationResponse):
    """Response: serialized gallery (ArtGalleryDict shape)."""

    id: str
    created_at: str
    updated_at: str
    boundary: list[Any]
    obstacles: dict[str, Any]
    owner_job_id: str
    title: str
    ears: dict[str, Any]
    convex_components: dict[str, Any]
    guards: dict[str, Any]
    visibility: dict[str, Any]


class JobMutationResponse(MutationResponse):
    """Response: serialized job (JobDict shape)."""

    id: str
    created_at: str
    updated_at: str
    parent_id: str | None
    children_ids: list[str]
    status: str
    step_name: str
    stdin: dict[str, Any]
    stdout: dict[str, Any]
    meta: dict[str, Any]
    stderr: dict[str, Any]


def gallery_id_from_job_and_user(job_id: Identifier, user_email: Email) -> Identifier:
    """
    Stable gallery id: Identifier of the Signature of the concatenation of job_id and user_email.

    For example, to derive gallery id from job and owner:
    >>> gid = gallery_id_from_job_and_user(Identifier("j1"), Email("u@e.com"))
    >>> str(gid)
    '...'
    """
    return Identifier(Signature(f"{job_id}_{user_email}"))


class Mutation(Controller):
    """
    Base mutation: validate, execute, handler. No user; use PrivateControllerMixin for auth.

    For example, to run a mutation (with user for private mutations):
    >>> handler = JobMutation(user=request.user)
    >>> result = handler.handler({"boundary": [...], "obstacles": []})
    """

    @abstractmethod
    def validate(self, body: dict[str, Any]) -> MutationRequest:
        pass

    @abstractmethod
    def execute(self, validated_input: MutationRequest) -> MutationResponse:
        pass


class JobMutation(PrivateControllerMixin, Mutation):
    """
    Create job (idempotent id from boundary+obstacles), save, enqueue run, update job index.

    For example, to create a job:
    >>> handler = JobMutation(user=request.user)
    >>> result = handler.handler({"boundary": [[0,0],[10,0],[10,10],[0,10]], "obstacles": []})
    >>> "id" in result
    True
    """

    def validate(self, body: dict[str, Any]) -> JobMutationRequest:
        super().validate(body)
        boundary = body.get("boundary")
        obstacles = body.get("obstacles")
        if not boundary or not isinstance(boundary, list):
            raise BoundaryRequiredError("boundary is required and must be a list of points")
        if obstacles is not None and not isinstance(obstacles, list):
            raise ObstaclesMustBeListError("obstacles must be a list of obstacle polygons")
        title = body.get("title")
        if title is not None and not isinstance(title, str):
            raise TitleMustBeStringError("title must be a string")
        title_str = str(title).strip() if title else "Untitled Gallery"
        return JobMutationRequest(
            boundary=Polygon.unserialize(boundary),
            obstacles=Table.unserialize([Polygon.unserialize(obs) for obs in (obstacles or []) if isinstance(obs, list)]),
            title=title_str,
        )

    def execute(self, validated_input: JobMutationRequest) -> JobMutationResponse:
        boundary = validated_input["boundary"]
        obstacles = validated_input["obstacles"]
        # Fail fast: run polygon validation and raise if any check fails.
        validation = PolygonValidation()
        validation_result = validation.execute({"boundary": boundary, "obstacles": obstacles})
        failed = [k for k, v in validation_result.items() if not k.endswith(".note") and v == "failed"]
        if failed:
            raise PolygonValidationError("Polygon validation failed: " + ", ".join(failed))
        job_id = Identifier(Signature(f"{hash(boundary)}_{hash(obstacles)}"))
        title = validated_input.get("title") or "Untitled Gallery"
        job = Job(
            id=job_id,
            stdin={
                "boundary": boundary.serialize(),
                "obstacles": [poly.serialize() for poly in obstacles],
            },
            meta={"title": title},
        )
        repo = JobsRepository(user=self.user)
        repo.save(job)
        email = self.user.email
        if email is None:
            raise UserNotAuthenticatedError("User must be authenticated")
        queue.put(Message(action=Action.START, job_id=job.id, user_email=email))
        index = JobsPrivateIndex(user_email=email)
        index.save(
            Indexed(
                index_id=Identifier(Countdown.from_timestamp(job.created_at)),
                real_id=job.id,
            )
        )
        logger.info("JobMutation.mutate() | created job_id=%s user=%s", job.id, email)
        return job.serialize()


class JobUpdateMutation(PrivateControllerMixin, Mutation):
    """
    Update job metadata; sync title to gallery if published.

    For example, to update job meta and title:
    >>> handler = JobUpdateMutation(user=request.user)
    >>> result = handler.handler({"id": "j1", "meta": {"title": "My Gallery"}})
    """

    def validate(self, body: dict[str, Any]) -> JobUpdateMutationRequest:
        super().validate(body)
        meta = body.get("meta")
        if meta is None:
            raise MetaRequiredError("meta is required")
        if not isinstance(meta, dict):
            raise MetaMustBeDictError("meta must be a dict")
        meta_str: dict[str, str] = {}
        for k, v in meta.items():
            if not isinstance(k, str):
                raise MetaKeysMustBeStringsError("meta keys must be strings")
            if v is not None and not isinstance(v, str):
                raise MetaValuesMustBeStringsError("meta values must be strings")
            meta_str[k] = str(v) if v is not None else ""
        return JobUpdateMutationRequest(
            job_id=Identifier(body.get("id")),
            meta=meta_str,
        )

    def execute(self, validated_input: JobUpdateMutationRequest) -> JobMutationResponse:
        job_id = validated_input["job_id"]
        meta = validated_input["meta"]
        email = self.user.email
        if email is None:
            raise UserNotAuthenticatedError("User must be authenticated")
        repo_job = JobsRepository(user=self.user)
        job = repo_job.get(job_id)
        job.meta = {**job.meta, **meta}
        repo_job.save(job)
        if "title" in meta:
            gallery_repo = ArtGalleryRepository()
            gallery_id = gallery_id_from_job_and_user(job_id, email)
            if gallery_repo.exists(gallery_id):
                gallery = gallery_repo.get(gallery_id)
                gallery.title = Title(meta["title"])
                gallery_repo.save(gallery)
        logger.info("JobUpdateMutation.mutate() | updated job_id=%s", job.id)
        return job.serialize()


class ArtGalleryPublishMutation(PrivateControllerMixin, Mutation):
    """
    Publish gallery from job stdout; user must own the job.

    For example, to publish after job completes:
    >>> handler = ArtGalleryPublishMutation(user=request.user)
    >>> result = handler.handler({"id": "job-123"})
    >>> "boundary" in result
    True
    """

    def validate(self, body: dict[str, Any]) -> ArtGalleryPublishMutationRequest:
        super().validate(body)
        return ArtGalleryPublishMutationRequest(job_id=Identifier(body.get("id")))

    def execute(self, validated_input: ArtGalleryPublishMutationRequest) -> ArtGalleryPublishMutationResponse:
        job_id = validated_input["job_id"]
        repo_job = JobsRepository(user=self.user)
        job = repo_job.get(job_id)
        if not job.is_finished():
            raise JobNotFinishedToPublishError("Job must be successfully finished to publish")
        boundary = job.stdout.get("boundary")
        if not boundary or not isinstance(boundary, list) or len(boundary) == 0:
            raise JobStdoutMissingGeometryError("Job stdout has no boundary or obstacles; cannot publish gallery")
        gallery_id = gallery_id_from_job_and_user(job_id, self.user.email)
        title: str = job.meta.get("title", "Untitled Art Gallery") if isinstance(job.meta.get("title"), str) else "Untitled Art Gallery"
        data: dict[str, Any] = {
            **job.stdout,
            "id": str(gallery_id),
            "owner_job_id": str(job_id),
            "title": title,
            "created_at": str(job.created_at),
            "updated_at": str(job.updated_at),
        }
        gallery = ArtGallery.unserialize(data)
        gallery_repo = ArtGalleryRepository()
        gallery_repo.save(gallery)
        index = ArtGalleryPublicIndex()
        index.save(
            Indexed(
                index_id=Identifier(Countdown.from_timestamp(gallery.created_at)),
                real_id=gallery.id,
            )
        )
        return gallery.serialize()


class JobDeleteMutation(PrivateControllerMixin, Mutation):
    """
    Delete a job by id. Recursively deletes children then the job and its index entry.

    For example, to delete a job:
    >>> handler = JobDeleteMutation(user=request.user)
    >>> result = handler.handler({"id": "job-123"})
    """

    def validate(self, body: dict[str, Any]) -> JobDeleteMutationRequest:
        super().validate(body)
        return JobDeleteMutationRequest(job_id=Identifier(body.get("id")))

    def execute(self, validated_input: JobDeleteMutationRequest) -> dict[str, Any]:
        email = self.user.email
        if email is None:
            raise UserNotAuthenticatedError("User must be authenticated")
        self._delete(validated_input["job_id"], email)
        return {}

    def _delete(self, job_id: Identifier, user_email: Email) -> None:
        from models import User

        repo = JobsRepository(user=User(email=user_email))
        try:
            job = repo.get(job_id)
        except RecordNotFoundError:
            return
        for child_id in job.children_ids:
            self._delete(child_id, user_email)
        if job.step_name == StepName.ART_GALLERY:
            index = JobsPrivateIndex(user_email=user_email)
            index.delete(Identifier(Countdown.from_timestamp(job.created_at)))
        repo.delete(job.id)
        logger.info("JobDeleteMutation._delete() | deleted job_id=%s user=%s", job_id, user_email)
