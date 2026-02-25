"""
Art gallery unpublish (hide) mutation.
"""

from __future__ import annotations

from typing import Any

from indexes.gallery import ArtGalleryPublicIndex
from repositories.gallery import ArtGalleryRepository
from repositories.jobs import JobsRepository
from attributes import Identifier
from attributes import Countdown

from mutations.private import PrivateMutation
from mutations.request import ArtGalleryHideMutationRequest
from mutations.utils import gallery_id_from_job_and_user


class ArtGalleryHideMutation(PrivateMutation[ArtGalleryHideMutationRequest, dict[str, Any]]):
    """Remove gallery from repo and public index; user must own the job."""

    def _validate_body(self, body: dict[str, Any]) -> ArtGalleryHideMutationRequest:
        return ArtGalleryHideMutationRequest(job_id=Identifier(body.get("job_id")))

    def mutate(self, validated_input: ArtGalleryHideMutationRequest) -> dict[str, Any]:
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
