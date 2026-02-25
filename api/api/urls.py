"""
URL mapping: path prefix -> method -> Query or Mutation class.
"""

from typing import Any

from mutations import JobMutation
from mutations import JobUpdateMutation
from queries import ArtGalleryDetailsQuery
from queries import ArtGalleryListQuery
from queries import JobDetailsQuery
from queries import JobListQuery

URLS: dict[str, dict[str, type]] = {
    "v1/galleries/": {"GET": ArtGalleryDetailsQuery},
    "v1/galleries": {"GET": ArtGalleryListQuery},
    "v1/jobs/": {"GET": JobDetailsQuery, "POST": JobUpdateMutation},
    "v1/jobs": {"GET": JobListQuery, "POST": JobMutation},
}
