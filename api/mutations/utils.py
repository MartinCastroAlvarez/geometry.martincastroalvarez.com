"""
Helpers for mutation payload coercion.
"""

from __future__ import annotations

import hashlib
from typing import Any

from attributes import Point
from geometry import ConvexComponent
from geometry import Ear
from geometry import Polygon


def gallery_id_from_job_and_user(job_id: str, user_email: str) -> str:
    digest = hashlib.sha256(user_email.encode()).hexdigest()
    return f"{job_id}_{digest}"


def coerce_boundary(value: Any) -> Polygon:
    """Build Polygon from list of point coords; validation via Polygon.unserialize (Point.unserialize)."""
    return Polygon.unserialize(value if isinstance(value, list) else [])


def coerce_obstacles(value: Any) -> list[Polygon]:
    """Build list of Polygon from list of obstacle point lists; validation via Polygon.unserialize."""
    if not isinstance(value, list):
        return []
    return [Polygon.unserialize(obs) for obs in value if isinstance(obs, list)]


def coerce_ears(value: Any) -> list[Ear]:
    """Build list of Ear from list of 3-point sequences; validation via Polygon.unserialize (Point.unserialize)."""
    if not isinstance(value, list):
        return []
    return [Ear(list(Polygon.unserialize(seq))) for seq in value if isinstance(seq, list)]


def coerce_convex(value: Any) -> list[ConvexComponent]:
    """Build list of ConvexComponent; validation via Polygon.unserialize (Point.unserialize)."""
    if not isinstance(value, list):
        return []
    return [ConvexComponent(list(Polygon.unserialize(comp))) for comp in value if isinstance(comp, list)]


def coerce_guards(value: Any) -> list[Point]:
    """Build list of Point; validation via Point.unserialize."""
    if not isinstance(value, list):
        return []
    return [Point.unserialize(p) for p in value]


def coerce_visibility(value: Any) -> dict[Point, list[Point]]:
    """Build visibility dict; keys and values validated via Point.unserialize."""
    if not isinstance(value, dict):
        return {}
    out: dict[Point, list[Point]] = {}
    for key, points in value.items():
        key_pt = Point.unserialize(key)
        out[key_pt] = [Point.unserialize(p) for p in points] if isinstance(points, list) else []
    return out
