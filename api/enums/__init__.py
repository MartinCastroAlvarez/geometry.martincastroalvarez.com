"""
API enums: Action, Method, Orientation, Stage, Status.

Title
-----
Enums Package

Context
-------
This package exports enums used across the API and workers. Method is
HTTP method (OPTIONS, GET, POST, PATCH, DELETE) with parse() that raises
MethodNotAllowedError. Action is worker action (START, REPORT) with parse()
defaulting to START. Status is task status (PENDING, SUCCESS, FAILED).
Stage is job pipeline stage (ART_GALLERY, STITCHING, EAR_CLIPPING, etc.).
Orientation is geometric turn direction (COLLINEAR, CLOCKWISE, COUNTER_CLOCKWISE).
All have parse() or value coercion where used in request/response.

Examples:
    Method.parse(request.http_method)
    Action.parse(body.get("action"))
    Status.parse(job_data.get("status"))
"""

from enums.action import Action
from enums.method import Method
from enums.orientation import Orientation
from enums.stage import Stage
from enums.status import Status

__all__ = ["Action", "Method", "Orientation", "Stage", "Status"]
