# API (Backend)

REST and worker backend for the geometry project: Lambda handlers, S3 bucket access, SQS queue, repositories, indexes, and typed models.

## Purpose

- **REST:** v1/galleries (list, get), v1/jobs (list, get, create, update, delete); CORS and path params; private endpoints via X-Auth/JWT.
- **Persistence:** S3 bucket (data/), repositories per entity (repositories/), indexes for “newest first” listing (index/, Countdown).
- **Async:** SQS queue for job run/report; worker Lambda (workers/) parses messages and runs tasks (tasks/).

## Requirements

- Python ≥ 3.13

## Folder contents

| Type | Files / packages |
|------|------------------|
| **Handlers** | `api.py` |
| **Core** | `exceptions.py`, `messages.py` |
| **Packages** | `api/api/`, `attributes/`, `data/`, `index/`, `interfaces/`, `models/`, `mutations/`, `queries/`, `repositories/`, `tasks/`, `workers/` |
| **Models** | `models/` (base.py: Model; art_gallery.py: ArtGallery; job.py: Job; user.py: User) |
| **Other** | `README.md`, `requirements.txt` |

## Modules and packages

| Module / package | Contents |
|------------------|----------|
| **api/** | Package; `api.handler` is the Lambda entry point. |
| **api/api/** | `request.py`: `Request`. `response.py`: `Response`. `private.py`: `private` decorator (X-Auth/JWT). `interceptor.py`: `interceptor` decorator (event→Request, response dict). `utils.py`: `extract_path_params()`. `urls.py`: `URLS` (path→method→Query/Mutation). `handler.py`: `handler` (routing, merge params, dispatch). |
| `exceptions.py` | `GeometryException`, `ValidationError`, `RecordNotFoundError`, `UnauthorizedError`, `ForbiddenError`, `InvalidActionError`, etc. |
| `messages.py` | `Message` (Serializable; action as `Action`), `Queue` (put, receive, delete, commit) |
| **data/** | `bucket.py`: `Bucket` (exists, load, save, delete, search), `DATA_BUCKET_NAME`. `page.py`: `Page`. `secret.py`: `Secret.get(secret_id)`, `SECRETS_BUCKET_NAME` |
| **models/** | `base.py`: `Model`. `art_gallery.py`: `ArtGallery`. `job.py`: `Job`. `user.py`: `User` (id, created_at, updated_at, to_dict/from_dict) |
| **interfaces/** | `Serializable` (to_dict, from_dict), `Measurable` (abstract size) |
| **attributes/** | `Timestamp`, `Countdown`, `Action` (RUN, REPORT), `Identifier`, `Limit`, `Point`, `Polygon[T]`, `Segment`, `Interval`, `Email`, `Url`, etc. |
| **index/** | `Indexed`, `Index[T]`, `PrivateIndex`, `ArtGalleryPublicIndex`, `JobsPrivateIndex` (REPOSITORY set in subclass; index modules: `gallery.py`, `jobs.py`) |
| **repositories/** | `Repository[T]`, `PrivateRepository[T]`, `Results[T]`, `ArtGalleryRepository`, `JobsRepository` |
| **queries/** | `Query[T]`, `ArtGalleryListQuery`, `ArtGalleryDetailsQuery`, `JobListQuery`, `JobDetailsQuery` |
| **mutations/** | `ArtGalleryPublishMutation`, `ArtGalleryHideMutation`, `JobMutation`, `JobUpdateMutation`. Modules: `base.py`, `gallery_publish.py`, `gallery_unpublish.py`, `jobs.py`, `utils.py`. Object ids in mutation inputs use `Identifier`, not `str`. |
| **tasks/** | `Task[T]`, `RunTask`, `ReportTask` (validate, execute, handle) |
| **workers/** | `Request`, `handler` (SQS event → dispatch by `Action` to RunTask/ReportTask, commit) |
