"""
URL mapping: Path -> method -> Query or Mutation class.

Title
-----
API Route Table (URLS)

Context
-------
URLS is the central route table for the API. Each key is a Path prefix
(e.g. "v1/galleries", "v1/jobs"); each value is a dict mapping Method
(GET, POST, PATCH, DELETE) to the Query or Mutation class that handles
that combination. The handler matches the request path by prefix and
method, then instantiates the class (with user for Private* handlers)
and calls handle(body). List vs detail routes are distinguished by
trailing slash and path segments (e.g. v1/galleries vs v1/galleries/
for a single gallery by id). OPTIONS is handled globally for CORS.

Examples:
>>> URLS[Path("v1/jobs")][Method.GET]  # JobListQuery
>>> URLS[Path("v1/jobs/")][Method.POST]  # ArtGalleryPublishMutation
"""

from typing import Type

from attributes import Path
from enums import Method
from mutations import ArtGalleryHideMutation
from mutations import ArtGalleryPublishMutation
from mutations import JobMutation
from mutations import JobUpdateMutation
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
        Method.PATCH: JobUpdateMutation,
        Method.DELETE: ArtGalleryHideMutation,
    },
    Path("v1/jobs"): {Method.GET: JobListQuery, Method.POST: JobMutation},
}
