"""
Art gallery publish and unpublish (hide) mutations.
"""

from __future__ import annotations

from typing import Any

from attributes import Countdown
from attributes import Identifier
from exceptions import ValidationError
from indexes.gallery import ArtGalleryPublicIndex
from indexes.indexed import Indexed
from models import ArtGallery
from mutations.private import PrivateMutation
from mutations.request import ArtGalleryHideMutationRequest
from mutations.request import ArtGalleryPublishMutationRequest
from mutations.response import ArtGalleryHideMutationResponse
from mutations.response import ArtGalleryPublishMutationResponse
from mutations.utils import gallery_id_from_job_and_user
from repositories.gallery import ArtGalleryRepository
from repositories.jobs import JobsRepository


class ArtGalleryPublishMutation(PrivateMutation[ArtGalleryPublishMutationRequest, ArtGalleryPublishMutationResponse]):
    """Publish gallery from job stdout; user must own the job."""

    def validate(self, body: dict[str, Any]) -> ArtGalleryPublishMutationRequest:
        super().validate(body)
        return ArtGalleryPublishMutationRequest(job_id=Identifier(body.get("id")))

    def mutate(self, validated_input: ArtGalleryPublishMutationRequest) -> ArtGalleryPublishMutationResponse:
        job_id = validated_input["job_id"]
        repo_job = JobsRepository(user=self.user)
        job = repo_job.get(job_id)
        if not job.is_finished():
            raise ValidationError("Job must be successfully finished to publish")
        gallery_id = gallery_id_from_job_and_user(job_id, self.user.email)
        title: str = job.meta.get("title", "Untitled Art Gallery") if isinstance(job.meta.get("title"), str) else "Untitled Art Gallery"
        data: dict[str, Any] = {
            **job.stdout,
            "id": str(gallery_id),
            "owner_email": str(self.user.email),
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


class ArtGalleryHideMutation(PrivateMutation[ArtGalleryHideMutationRequest, ArtGalleryHideMutationResponse]):
    """Remove gallery from repo and public index; user must own the job."""

    def validate(self, body: dict[str, Any]) -> ArtGalleryHideMutationRequest:
        super().validate(body)
        return ArtGalleryHideMutationRequest(job_id=Identifier(body.get("id")))

    def mutate(self, validated_input: ArtGalleryHideMutationRequest) -> ArtGalleryHideMutationResponse:
        job_id = validated_input["job_id"]
        repo_job = JobsRepository(user=self.user)
        repo_job.get(job_id)
        gallery_id = gallery_id_from_job_and_user(job_id, self.user.email)
        gallery_repo = ArtGalleryRepository()
        gallery = gallery_repo.get(gallery_id)
        index = ArtGalleryPublicIndex()
        index_id = Identifier(Countdown.from_timestamp(gallery.created_at))
        if index.exists(index_id):
            index.delete(index_id)
        gallery_repo.delete(gallery_id)
        return {"deleted": True, "id": str(gallery_id)}
