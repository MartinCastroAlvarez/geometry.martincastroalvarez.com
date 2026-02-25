# API (Backend)

REST and worker backend for the geometry project: Lambda handlers, S3 bucket access, SQS queue, repositories, indexes, and typed models.

## Purpose

- **REST:** v1/galleries (list, get), v1/jobs (list, get, create, update, delete); CORS and path params; private endpoints via X-Auth/JWT.
- **Persistence:** S3 bucket (data/), repositories per entity (repositories/), indexes for “newest first” listing (indexes/, Countdown).
- **Async:** SQS queue for job run/report; worker Lambda (workers/) parses messages and runs tasks (tasks/).

## Requirements

- Python ≥ 3.13

## Folder contents

| Type | Files / packages |
|------|------------------|
| **Handlers** | `api.py` |
| **Core** | `exceptions.py`, `messages/` |
| **Packages** | `api/api/`, `attributes/`, `data/`, `enums/`, `indexes/`, `interfaces/`, `models/`, `mutations/`, `queries/`, `repositories/`, `structs/`, `tasks/`, `workers/` |
| **Models** | `models/` (base.py: Model; art_gallery.py: ArtGallery; job.py: Job; user.py: User) |
| **Other** | `README.md`, `requirements.txt` |

## Modules and packages

| Module / package | Contents |
|------------------|----------|
| **api/** | Package; `api.handler` is the Lambda entry point. |
| **api/api/** | `request.py`: `ApiRequest` (path as `Path`, normalized; method, headers, body, path_params, query_params, user). `response.py`: `Response`. `private.py`: `private` decorator (X-Auth/JWT). `interceptor.py`: `interceptor` decorator (event→ApiRequest, response dict). `urls.py`: `URLS` as `dict[Path, dict[Method, Query | Mutation]]` (keys e.g. `Path("v1/galleries/")`, `Path("v1/galleries")`). `handler.py`: `handler` (match path to URLS, set path_params from `path.id` for detail routes, merge params, dispatch). |
| `exceptions.py` | `GeometryException`, `ValidationError`, `RecordNotFoundError`, `UnauthorizedError`, `ForbiddenError`, `InvalidActionError`, `PathMissingResourceIdError` (path without resource id), etc. |
| **messages/** | `message.py`: `Message` (Serializable; action as `Action` from enums). `queue.py`: `Queue` (put, receive, delete, commit). |
| **data/** | `bucket.py`: `Bucket` (exists, load, save, delete, search), `DATA_BUCKET_NAME`. `page.py`: `Page`. `secret.py`: `Secret.get(secret_id)`, `SECRETS_BUCKET_NAME` |
| **models/** | `base.py`: `Model`. `art_gallery.py`: `ArtGallery`. `job.py`: `Job`. `user.py`: `User` (id, email non-nullable, to_dict/from_dict) |
| **interfaces/** | `Serializable` (to_dict, from_dict), `Measurable` (abstract size) |
| **enums/** | `action.py`: `Action` (START, REPORT; default START) with `parse()`. `method.py`: `Method` (GET, POST, OPTIONS, etc.) with `parse()`. `status.py`: `Status` (PENDING, SUCCESS, FAILED) with `parse()`. `orientation.py`: `Orientation`. |
| **attributes/** | Value types: `Timestamp`, `Countdown`, `Identifier`, `Limit`, `Email`, `Url`, `Signature`, `Slug`, `Interval`, `Path` (str subclass; normalized API path with `.version`, `.resource`, `.id`; raises `PathMissingResourceIdError` when id missing). Geometry types (Box, Point, Polygon, Segment, Walk, etc.) re-exported from geometry. |
| **structs/** | **Data structures.** `sequence.py`: `Sequence[T]` (list-like with modular slicing, shift, hash, add/sub/__and__/invert, serialize/unserialize). `table.py`: `Table[T]` (dict-like keyed by `hash(item)`; add/+=, pop/-=; `Serializable[dict]`; serialize→dict, unserialize from list of items or dict with key=hash(value) or raise). |
| **indexes/** | `Indexed`, `Index[T]`, `PrivateIndex`, `ArtGalleryPublicIndex`, `JobsPrivateIndex` (REPOSITORY set in subclass; index modules: `gallery.py`, `jobs.py`) |
| **repositories/** | `base.py`: `Repository[T]`. `private.py`: `PrivateRepository[T]`. `results.py`: `Results[T]`. `ArtGalleryRepository`, `JobsRepository`. |
| **queries/** | `Query[T]`, `ArtGalleryListQuery`, `ArtGalleryDetailsQuery`, `JobListQuery`, `JobDetailsQuery` |
| **mutations/** | `ArtGalleryPublishMutation`, `ArtGalleryHideMutation`, `JobMutation` (create only). Modules: `base.py`, `gallery_publish.py`, `gallery_unpublish.py`, `jobs.py`. Publish uses `ArtGallery.unserialize`; job create uses `Polygon.unserialize` and `Table.unserialize` inline. Object ids use `Identifier`. |
| **tasks/** | `Task[T]`, `StartTask`, `ReportTask` (validate, execute, handle; report sets job success/failed from children, enqueues parent REPORT) |
| **workers/** | `request.py`: `WorkerRequest` (action, job_id, user_email, body, message). `response.py`: `WorkerResponse`. `handler`: SQS event → dispatch by `Action` to StartTask/ReportTask, commit each message; returns `WorkerResponse`. `urls.py`: `TASK_BY_ACTION`. |
