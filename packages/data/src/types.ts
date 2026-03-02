/**
 * API response types and shared shapes for the data layer.
 *
 * Context: These types mirror backend responses (session, geometry jobs/galleries).
 * Used by adapters (fromApi*, toDomain*) and API clients. Domain types (Job, Gallery,
 * User) live in @geometry/domain; here we only define the wire format.
 *
 * Example:
 *   const raw: unknown = await response.json();
 *   const apiJob = fromApiJob(raw);   // ApiJob
 *   const apiGallery = fromApiArtGallery(raw);  // ApiArtGallery
 */

/** User - matches session API response */
export interface ApiUser {
    email: string | null;
    name: string | null;
    avatarUrl: string | null;
}

/** Job - matches geometry API job response. stdin/stdout may contain boundary, obstacles, stitched, guards, visibility, etc.; coordinates may be numbers or numeric strings. */
export interface ApiJob {
    id: string;
    parent_id: string | null;
    children_ids: string[];
    status: string;
    step_name: string;
    stdin: Record<string, unknown>;
    stdout: Record<string, unknown>;
    meta: Record<string, unknown>;
    stderr: Record<string, unknown>;
    created_at: string;
    updated_at: string;
}

export interface ApiPoint {
    x: number;
    y: number;
}

export interface ApiPolygon {
    points: ApiPoint[];
}

/** ArtGallery - matches geometry API gallery response */
export interface ApiArtGallery {
    id: string;
    boundary: ApiPolygon;
    obstacles: Record<string, ApiPolygon>;
    owner_job_id: string;
    title?: string;
    ears?: Record<string, unknown>;
    convex_components?: Record<string, unknown>;
    guards?: Record<string, ApiPoint>;
    visibility?: Record<string, ApiPoint[]>;
    /** Optional stitched polygon (list of points or { points } from API). */
    stitched?: ApiPolygon | Array<{ x: number; y: number } | [number, number]>;
    /** Optional list of bridge edges from stitching step; each segment is [[x,y],[x,y]]. */
    stitches?: Array<Array<{ x: number; y: number } | [number, number]>>;
    created_at: string;
    updated_at: string;
}

/** List endpoint response: array of entities under `data` and optional next_token (e.g. jobs list, galleries list). */
export interface ListResponse<T> {
    data: T[];
    next_token: string;
}

/** Details endpoint response: single entity under `data`. */
export interface DetailsResponse<T> {
    data: T;
}

export interface SessionResponse {
    email: string | null;
    name: string | null;
    avatarUrl: string | null;
}

export interface GeometryApiJob {
    id: string;
    parent_id: string | null;
    children_ids: string[];
    status: string;
    step_name: string;
    stdin: Record<string, unknown>;
    stdout: Record<string, unknown>;
    meta: Record<string, unknown>;
    stderr: Record<string, unknown>;
    created_at: string;
    updated_at: string;
}

export interface GeometryApiArtGallery {
    id: string;
    boundary: { points: Array<{ x: number; y: number }> };
    obstacles: Record<string, unknown>;
    owner_job_id: string;
    title: string;
    ears?: Record<string, unknown>;
    convex_components?: Record<string, unknown>;
    guards?: Record<string, unknown>;
    visibility?: Record<string, unknown>;
    created_at: string;
    updated_at: string;
}

/** Polygon validation response: keys like "polygon.convex", "polygon.convex.note", "obstacles.0.contained"; values are status ("pending"|"success"|"failed") or note strings. */
export type PolygonValidationResponse = Record<string, string>;

/** API error response shape (e.g. 400 ValidationError). */
export interface ApiErrorResponse {
    error: {
        code: number;
        type: string;
        message: string;
    };
}
