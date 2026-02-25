"""
Stage enum for job pipeline stages.
"""

from __future__ import annotations

from enum import Enum

from exceptions import ValidationError


class Stage(str, Enum):
    """Job pipeline stage."""

    ART_GALLERY = "art_gallery"
    STITCHING = "stitching"
    EAR_CLIPPING = "ear_clipping"
    CONVEX_COMPONENT_OPTIMIZATION = "convex_component_optimization"
    VISIBILITY_MATRIX = "visibility_matrix"
    GUARD_PLACEMENT = "guard_placement"

    @classmethod
    def parse(cls, value: str | None) -> Stage:
        """Coerce string to Stage; raises ValidationError (400) if invalid."""
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError("stage is required and must be a non-empty string")
        raw: str = value.strip().lower().replace(" ", "_") if isinstance(value, str) else str(value).strip().lower().replace(" ", "_")
        try:
            return cls(raw)
        except ValueError:
            allowed = ", ".join(repr(s.value) for s in cls)
            raise ValidationError(f"stage must be one of [{allowed}], got {raw!r}")
