"""
URL mapping: Path -> method -> Query or Mutation class.
"""

from typing import Type

from attributes import Path
from enums import Method
from mutations import ArtGalleryHideMutation
from mutations import ArtGalleryPublishMutation
from mutations import JobMutation
from mutations.base import Mutation
from queries import ArtGalleryDetailsQuery
from queries import ArtGalleryListQuery
from queries import JobDetailsQuery
from queries import JobListQuery
from queries.base import Query

URLS: dict[Path, dict[Method, Type[Query | Mutation]]] = {
    Path("v1/galleries/"): {Method.GET: ArtGalleryDetailsQuery},
    Path("v1/galleries"): {Method.GET: ArtGalleryListQuery},
    Path("v1/jobs/"): {
        Method.GET: JobDetailsQuery,
        Method.POST: ArtGalleryPublishMutation,
        Method.DELETE: ArtGalleryHideMutation,
    },
    Path("v1/jobs"): {Method.GET: JobListQuery, Method.POST: JobMutation},
}
