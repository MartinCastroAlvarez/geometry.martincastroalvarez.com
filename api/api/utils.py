"""
API utilities: extract_path_params from request path and route pattern.
"""

from __future__ import annotations

import re


def extract_path_params(request_path: str, route_pattern: str) -> dict[str, str]:
    """
    Extract path parameters from a request path using a route pattern.

    For example:
    >>> extract_path_params("/v1/galleries/abc123", "/v1/galleries/{id}")
    {"id": "abc123"}
    >>> extract_path_params("/v1/jobs/xyz", "/v1/jobs/{id}")
    {"id": "xyz"}
    """
    param_names = re.findall(r"\{([^}]+)\}", route_pattern)
    regex_pattern = re.sub(r"\{[^}]+\}", r"([^/]+)", route_pattern)
    regex_pattern = f"^{regex_pattern}$"
    match = re.match(regex_pattern, request_path.strip("/"))
    if not match:
        return {}
    param_values = match.groups()
    return dict(zip(param_names, param_values))
