"""
Pytest configuration. Mocks boto3/botocore and jwt so api can be imported without Lambda deps.
Run tests with: PYTHONPATH=api poetry run pytest tests/ -v
"""

import os
import sys
from unittest.mock import MagicMock

# Avoid ConfigurationError when handler or index need bucket names (unit tests still mock S3)
os.environ.setdefault("DATA_BUCKET_NAME", "test-data-bucket")
os.environ.setdefault("SECRETS_BUCKET_NAME", "test-secrets-bucket")

# Allow api package to load without boto3/jwt (e.g. in local pytest without Lambda deps)
if "boto3" not in sys.modules:
    sys.modules["boto3"] = MagicMock()
if "botocore" not in sys.modules:
    sys.modules["botocore"] = MagicMock()
    sys.modules["botocore.exceptions"] = MagicMock()
if "jwt" not in sys.modules:
    _jwt = MagicMock()
    _jwt.decode = lambda payload, key, algorithms: {"email": "test@test.com", "name": "", "avatarUrl": None}
    _jwt.ExpiredSignatureError = Exception
    _jwt.InvalidTokenError = Exception
    sys.modules["jwt"] = _jwt
