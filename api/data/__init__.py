"""
Data layer: S3 bucket, pagination page, and secrets.

Title
-----
Data Package (Storage and Secrets)

Context
-------
This package provides storage and configuration access for the geometry API.
Bucket wraps S3 for the data bucket (DATA_BUCKET_NAME): load/save/delete
JSON objects by key, and search with prefix and pagination (Page). Page
holds keys and next_token from list_objects_v2. Secret reads secret values
from S3 (SECRETS_BUCKET_NAME), e.g. JWT_SECRET and JWT_TEST, with per-Lambda
caching. All raise appropriate exceptions (ConfigurationError, ServiceUnavailableError,
ValidationError, NotFoundError) on missing env, S3 errors, or invalid input.

Examples:
>>> bucket = Bucket()
>>> bucket.save("data/galleries/abc.json", gallery.serialize())
>>> data = bucket.load("data/galleries/abc.json")
>>> page = bucket.search(prefix="data/galleries/", limit=Limit(20))
>>> secret = Secret.get(Secret.JWT_SECRET_NAME)
"""

from data.bucket import DATA_BUCKET_NAME
from data.bucket import Bucket
from data.page import Page
from data.secret import SECRETS_BUCKET_NAME
from data.secret import Secret

__all__ = [
    "Bucket",
    "DATA_BUCKET_NAME",
    "Page",
    "Secret",
    "SECRETS_BUCKET_NAME",
]
