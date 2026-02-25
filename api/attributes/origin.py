"""
Origin type: CORS origin string validated for API responses.
"""

from __future__ import annotations

from typing import Any


class Origin(str):
    """
    CORS origin string. Normalizes according to allowed patterns:
    - Empty or invalid -> "*"
    - https://*.martincastroalvarez.com -> as-is
    - http://localhost or http://localhost:* -> as-is
    - Other -> "https://geometry.martincastroalvarez.com"

    Example:
    >>> Origin("https://geometry.martincastroalvarez.com")
    'https://geometry.martincastroalvarez.com'
    >>> Origin("")
    '*'
    >>> Origin("http://localhost:3000")
    'http://localhost:3000'
    """

    def __new__(cls, value: Any = None) -> Origin:
        if value is None:
            return super().__new__(cls, "*")
        raw = str(value).strip() if value else ""
        if not raw:
            return super().__new__(cls, "*")
        if raw.startswith("https://") and raw.endswith(".martincastroalvarez.com"):
            return super().__new__(cls, raw)
        if raw.startswith("http://localhost:") or raw == "http://localhost":
            return super().__new__(cls, raw)
        return super().__new__(cls, "https://geometry.martincastroalvarez.com")
