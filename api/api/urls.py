"""
URL mapping: path prefix -> method -> Query or Mutation class.
"""

from mutations import JobMutation
from queries import ArtGalleryDetailsQuery
from queries import ArtGalleryListQuery
from queries import JobDetailsQuery
from queries import JobListQuery

from enums import Method

URLS: dict[str, dict[Method, type]] = {
    "v1/galleries/": {Method.GET: ArtGalleryDetailsQuery},
    "v1/galleries": {Method.GET: ArtGalleryListQuery},
    "v1/jobs/": {Method.GET: JobDetailsQuery},
    "v1/jobs": {Method.GET: JobListQuery, Method.POST: JobMutation},
}
