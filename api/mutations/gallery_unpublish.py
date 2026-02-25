"""
Art gallery unpublish (hide) mutation.
"""

from __future__ import annotations

from typing import Any

from exceptions import ForbiddenError
from exceptions import RecordNotFoundError
from exceptions import UnauthorizedError
from exceptions import ValidationError
from index.gallery import ArtGalleryPublicIndex
from repositories.gallery import ArtGalleryRepository
from repositories.jobs import JobsRepository
from attributes import Identifier
from attributes import Countdown

from mutations.base import Mutation
from mutations.base import MutationInput
from mutations.utils import gallery_id_from_job_and_user


class ArtGalleryHideMutationInput(MutationInput):
    """Hide: job_id required; gallery id derived from job id + hash(user email)."""

    job_id: Identifier


class ArtGalleryHideMutation(Mutation[ArtGalleryHideMutationInput]):
    """Remove gallery from repo and public index; user must own the job."""

    def validate(self, body: dict[str, Any] | None = None) -> ArtGalleryHideMutationInput:
        if not self.user.is_authenticated():
            raise UnauthorizedError("User must be authenticated")
        payload = body or {}
        job_id_raw = payload.get("job_id")
        if not job_id_raw or not isinstance(job_id_raw, str):
            raise ValidationError("job_id is required and must be a non-empty string")
        return ArtGalleryHideMutationInput(job_id=Identifier(job_id_raw))

    def mutate(self, validated_input: ArtGalleryHideMutationInput) -> dict[str, Any]:
        job_id = validated_input["job_id"]
        repo_job = JobsRepository(user=self.user)
        try:
            repo_job.get(job_id)
        except RecordNotFoundError:
            raise ForbiddenError("Job not found or access denied")
        gallery_id = gallery_id_from_job_and_user(str(job_id), self.user.email)
        gallery_repo = ArtGalleryRepository()
        try:
            gallery = gallery_repo.get(gallery_id)
        except RecordNotFoundError:
            return {"deleted": True, "id": gallery_id}
        index = ArtGalleryPublicIndex()
        index_id = Identifier(str(Countdown.from_timestamp(gallery.created_at)))
        if index.exists(index_id):
            index.delete(index_id)
        gallery_repo.delete(gallery_id)
        return {"deleted": True, "id": gallery_id}
