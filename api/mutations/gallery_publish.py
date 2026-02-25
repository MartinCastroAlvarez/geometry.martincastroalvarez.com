"""
Art gallery publish mutation.
"""

from __future__ import annotations

from typing import Any

from exceptions import ForbiddenError
from exceptions import RecordNotFoundError
from exceptions import UnauthorizedError
from exceptions import ValidationError
from index.gallery import ArtGalleryPublicIndex
from index.indexed import Indexed
from models import ArtGallery
from repositories.gallery import ArtGalleryRepository
from repositories.jobs import JobsRepository
from attributes import Identifier
from attributes import Countdown

from mutations.base import Mutation
from mutations.request import MutationRequest
from mutations.utils import coerce_boundary
from mutations.utils import coerce_convex
from mutations.utils import coerce_ears
from mutations.utils import coerce_guards
from mutations.utils import coerce_obstacles
from mutations.utils import coerce_visibility
from mutations.utils import gallery_id_from_job_and_user


class ArtGalleryPublishMutationInput(MutationRequest):
    """Publish: job_id required; gallery data taken from job stdout."""

    job_id: Identifier


class ArtGalleryPublishMutation(Mutation[ArtGalleryPublishMutationInput]):
    """Publish gallery from job stdout; user must own the job."""

    def validate(self, body: dict[str, Any] | None = None) -> ArtGalleryPublishMutationInput:
        if not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        payload = body or {}
        job_id_raw = payload.get("job_id")
        if not job_id_raw or not isinstance(job_id_raw, str):
            raise ValidationError("job_id is required and must be a non-empty string")
        return ArtGalleryPublishMutationInput(job_id=Identifier(job_id_raw))

    def mutate(self, validated_input: ArtGalleryPublishMutationInput) -> dict[str, Any]:
        job_id = validated_input["job_id"]
        repo_job = JobsRepository(user=self.user)
        try:
            job = repo_job.get(job_id)
        except RecordNotFoundError:
            raise ForbiddenError("Job not found or access denied")
        if not job.stdout:
            raise ValidationError("Job has no stdout; cannot publish")
        stdout = job.stdout
        gallery_id = gallery_id_from_job_and_user(str(job_id), self.user.email)
        if not self.user.is_authenticated():
            raise ValidationError("User email required to publish")
        gallery = ArtGallery(
            id=Identifier(gallery_id),
            boundary=coerce_boundary(stdout.get("boundary")),
            obstacles=coerce_obstacles(stdout.get("obstacles")),
            owner_email=self.user.email,
            owner_job_id=Identifier(str(job_id)),
            ears=coerce_ears(stdout.get("ears")),
            convex_components=coerce_convex(stdout.get("convex_components")),
            guards=coerce_guards(stdout.get("guards")),
            visibility=coerce_visibility(stdout.get("visibility")),
        )
        gallery_repo = ArtGalleryRepository()
        gallery_repo.save(gallery)
        index = ArtGalleryPublicIndex()
        index.save(Indexed(index_id=Identifier(str(Countdown.from_timestamp(gallery.created_at))), real_id=gallery.id))
        return gallery.serialize()
