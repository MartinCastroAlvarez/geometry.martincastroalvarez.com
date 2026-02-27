# API (Backend)

REST and worker backend for the geometry project: Lambda handlers, S3 bucket access, SQS queue, repositories, indexes, and typed models.

## Purpose

- **REST:** v1/galleries (list, get), v1/jobs (list, get, create, update, delete); CORS and path params; private endpoints via X-Auth/JWT.
- **Persistence:** S3 bucket (data.py), repositories per entity (repositories.py), indexes for “newest first” listing (indexes.py, Countdown).
- **Async:** SQS queue for job run/report; worker Lambda (workers.py) parses messages and runs tasks (tasks.py, tasks/).

## Requirements

- Python ≥ 3.13

## Structure

```
api/
├── __init__.py          # Package; exports handler (Lambda entry for API Gateway)
├── api.py               # API Gateway: ApiRequest, ApiResponse, ROUTES, private, interceptor, handler
├── workers.py           # SQS worker: ROUTES (Action→Task), WorkerRequest, WorkerResponse, handler
├── attributes.py        # Value types: Path, Identifier, Email, Timestamp, etc.; geometry re-exports
├── controllers.py       # Controller base, PrivateControllerMixin
├── data.py              # Bucket, Page, Secret
├── enums.py             # Action, Method, Status, Stage, Orientation
├── exceptions.py        # GeometryException, ValidationError, UnauthorizedError, etc.
├── indexes.py           # Index, ArtGalleryPublicIndex, JobsPrivateIndex
├── interfaces.py        # Serializable, Measurable, Bounded, Spatial, Volume
├── logger.py            # get_logger, log_extra
├── messages.py          # Message, Queue
├── models.py            # Model, User, Job, ArtGallery
├── mutations.py         # Mutation base; mutations/galleries.py, mutations/jobs.py
├── queries.py           # Query base; queries/galleries.py, queries/jobs.py
├── repositories.py      # Repository, ArtGalleryRepository, JobsRepository
├── serializers.py       # Serialized (parent), ModelDict, UserDict, JobDict, ArtGalleryDict
├── settings.py          # Env config: DATA_BUCKET_NAME, QUEUE_NAME, JWT_*, etc.
├── structs.py           # Sequence, Table
├── tasks.py             # Task base; tasks/start.py, tasks/report.py
├── validations.py       # Validation, PolygonValidation
├── geometry/            # 2D geometry: Point, Segment, Polygon, Box, Ear, ConvexComponent, Walk
│   ├── __init__.py
│   ├── box.py
│   ├── convex.py
│   ├── ear.py
│   ├── interval.py
│   ├── point.py
│   ├── polygon.py
│   ├── segment.py
│   └── walk.py
├── models/
│   └── user.py          # User model (auth); also defined in models.py
├── mutations/
│   ├── galleries.py      # ArtGalleryPublishMutation, ArtGalleryHideMutation
│   └── jobs.py          # JobMutation, JobUpdateMutation
├── queries/
│   ├── galleries.py     # ArtGalleryListQuery, ArtGalleryDetailsQuery
│   └── jobs.py          # JobListQuery, JobDetailsQuery
└── tasks/
    ├── start.py         # StartTask
    └── report.py        # ReportTask
```

## Lambda entry points

| Lambda   | Handler string   | Module / file   |
|----------|------------------|-----------------|
| API      | `api.handler`     | `__init__.py` → `api.api.handler` |
| Worker   | `workers.handler` | `workers.py`    |

## Modules and packages

| Module / package | Contents |
|------------------|----------|
| **api** (package) | `__init__.py` exports `handler`; Lambda entry for API Gateway. |
| **api.py** | `ApiRequest`, `ApiResponse`, `ROUTES` (`dict[Path, dict[Method, Controller]]`), `private` decorator (X-Auth/JWT), `interceptor` decorator (event→ApiRequest, response dict), `handler` (match path to ROUTES, instantiate controller, call `controller.handler(body)`). |
| **workers.py** | `ROUTES` (Action → Task), `WorkerRequest`, `WorkerResponse`, `handler`: SQS event → dispatch by Action to StartTask/ReportTask, commit each message; returns `WorkerResponse`. |
| **controllers.py** | **Controller** (abstract), **ControllerRequest**, **ControllerResponse**, **PrivateControllerMixin**. `validate(body) -> ControllerRequest`, `execute(ControllerRequest) -> ControllerResponse`, `handler(body) -> ControllerResponse`. Queries, mutations, validations, and tasks extend Controller. |
| **exceptions.py** | `GeometryException`, `ValidationError`, `RecordNotFoundError`, `UnauthorizedError`, `ForbiddenError`, `InvalidActionError`, `PathMissingResourceIdError`, etc. |
| **messages.py** | `Message` (Serializable; action as `Action`). `Queue` (put, receive, delete, commit). |
| **data.py** | `Bucket` (exists, load, save, delete, search), `Page`, `Secret`. Bucket and secret names from `settings`. |
| **settings.py** | `DATA_BUCKET_NAME`, `SECRETS_BUCKET_NAME`, `QUEUE_NAME`, `LOG_LEVEL`, `JWT_SECRET_NAME`, `JWT_TEST_NAME`, `DEFAULT_LIMIT`, etc. |
| **models.py** | `Model`, `User`, `Job`, `ArtGallery` (Serializable[Serialized] for S3/API). |
| **models/user.py** | User model (auth); used by api.api.private, JobsRepository, mutation/query handlers. |
| **serializers.py** | `Serialized` (parent TypedDict for Serializable[T]), `ModelDict`, `UserDict`, `JobDict`, `ArtGalleryDict`. |
| **interfaces.py** | `Serializable[T]`, `Measurable`, `Bounded`, `Spatial`, `Volume`. |
| **enums.py** | `Action` (START, REPORT), `Method` (GET, POST, …), `Status`, `Stage`, `Orientation` (with `parse()` where used). |
| **attributes.py** | `Timestamp`, `Countdown`, `Identifier`, `Limit`, `Email`, `Url`, `Signature`, `Slug`, `Interval`, `Path` (normalized API path; `.version`, `.resource`, `.id`; raises `PathMissingResourceIdError` when id missing). Geometry types re-exported from `geometry` via `__getattr__`. |
| **structs.py** | `Sequence[T]` (list-like; slicing, shift, hash, serialize/unserialize). `Table[T]` (dict-like keyed by `hash(item)`; Serializable[dict]). |
| **repositories.py** | `Repository[T]`, `Results[T]`, `PrivateRepository[T]`, `ArtGalleryRepository`, `JobsRepository`. |
| **indexes.py** | `Indexed`, `Index[T]`, `PrivateIndex`, `ArtGalleryPublicIndex`, `JobsPrivateIndex`. |
| **queries.py** | `Query`, `ListQuery`, `DetailsQuery`; **queries/galleries.py**: `ArtGalleryListQuery`, `ArtGalleryDetailsQuery`; **queries/jobs.py**: `JobListQuery`, `JobDetailsQuery`. Registered in api.api ROUTES. |
| **mutations.py** | `Mutation`; **mutations/galleries.py**: `ArtGalleryPublishMutation`, `ArtGalleryHideMutation`; **mutations/jobs.py**: `JobMutation`, `JobUpdateMutation`. Registered in api.api ROUTES. |
| **validations.py** | `Validation`, `PolygonValidation`. Registered in api.api ROUTES. |
| **tasks.py** | `Task` base; **tasks/start.py**: `StartTask`; **tasks/report.py**: `ReportTask`. Used by workers.py ROUTES. |
| **geometry/** | `Point`, `Segment`, `Polygon`, `Box`, `Interval`, `Walk`, `Ear`, `ConvexComponent`. Spatial, Bounded, Measurable, Volume, Serializable. Used by models.ArtGallery and pipeline (ear clipping, visibility, guards). |

## Other files

- **README.md** (this file)
- **requirements.txt** (boto3, botocore, PyJWT)
