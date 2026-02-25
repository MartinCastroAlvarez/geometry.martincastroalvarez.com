"""
Helpers for mutation payload coercion.
"""

from __future__ import annotations

import hashlib
from typing import Any

from attributes import Point
from attributes import Polygon


def gallery_id_from_job_and_user(job_id: str, user_email: str) -> str:
    digest = hashlib.sha256(user_email.encode()).hexdigest()
    return f"{job_id}_{digest}"


def coerce_boundary(value: Any) -> list[tuple[str, str]]:
    if not value:
        return []
    if isinstance(value, list):
        return [
            tuple(str(x) for x in p[:2]) if isinstance(p, (list, tuple)) and len(p) >= 2 else ("0", "0")
            for p in value
        ]
    return []


def coerce_obstacles(value: Any) -> list[list[tuple[str, str]]]:
    if not value:
        return []
    out: list[list[tuple[str, str]]] = []
    for obs in value:
        if isinstance(obs, list):
            out.append([
                tuple(str(x) for x in p[:2]) if isinstance(p, (list, tuple)) and len(p) >= 2 else ("0", "0")
                for p in obs
            ])
        else:
            out.append([])
    return out


def coerce_ears(value: Any) -> list[Polygon[Point]]:
    if not value or not isinstance(value, list):
        return []
    return [
        Polygon.from_list(seq, Point.from_list) if isinstance(seq, list) else Polygon([])
        for seq in value
    ]


def coerce_convex(value: Any) -> list[Polygon[Point]]:
    if not value or not isinstance(value, list):
        return []
    return [
        Polygon.from_list(comp, Point.from_list) if isinstance(comp, list) else Polygon([])
        for comp in value
    ]


def coerce_guards(value: Any) -> list[Point]:
    if not value or not isinstance(value, list):
        return []
    return [
        Point.from_list(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else Point(["0", "0"])
        for p in value
    ]


def coerce_visibility(value: Any) -> dict[Point, list[Point]]:
    if not value or not isinstance(value, dict):
        return {}
    out: dict[Point, list[Point]] = {}
    for key, points in value.items():
        if isinstance(key, (list, tuple)) and len(key) >= 2:
            key_pt = Point.from_list(key)
        else:
            parts = str(key).split(",")
            key_pt = Point.from_list(parts) if len(parts) >= 2 else Point(["0", "0"])
        if isinstance(points, list):
            out[key_pt] = [
                Point.from_list(p) if isinstance(p, (list, tuple)) and len(p) >= 2 else Point(["0", "0"])
                for p in points
            ]
        else:
            out[key_pt] = []
    return out
