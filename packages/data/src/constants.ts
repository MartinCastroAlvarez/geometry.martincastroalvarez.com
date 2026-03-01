/**
 * API base URLs, auth redirect, React Query stale times and query keys for the data layer.
 *
 * Context: Geometry API serves jobs and galleries; session API serves /v1/session.
 * AUTH_REDIRECT_URL is where users are sent to log in (useLogout in session.ts).
 * STALE_TIME_* and *_QUERY_KEY are used by job.ts, gallery.ts, session.ts and
 * ReactQueryProvider; all cache durations and query key roots live here.
 */

export const GEOMETRY_API_URL = "https://geometry.api.martincastroalvarez.com";
export const SESSION_API_URL = "https://login.api.martincastroalvarez.com";
export const AUTH_REDIRECT_URL = "https://login.martincastroalvarez.com";

export const SESSION_QUERY_KEY = ["session"] as const;
export const JOBS_QUERY_KEY = ["jobs"] as const;
export const JOB_QUERY_KEY = (jobId: string) => ["jobs", jobId] as const;
export const JOB_CHILDREN_QUERY_KEY = (jobIds: string[]) => ["jobs", "children", jobIds.join(",")] as const;
export const GALLERIES_QUERY_KEY = ["galleries"] as const;
export const GALLERY_QUERY_KEY = (galleryId: string) => ["galleries", galleryId] as const;

export const STALE_TIME_DEFAULT_MS = 5 * 60 * 1000;
export const STALE_TIME_JOBS_LIST_MS = 30 * 1000;
export const STALE_TIME_JOB_MS = 5 * 1000;
export const STALE_TIME_GALLERIES_LIST_MS = 2 * 60 * 1000;
export const STALE_TIME_GALLERY_MS = 60 * 1000;
export const STALE_TIME_SESSION_MS = 15 * 60 * 1000;
