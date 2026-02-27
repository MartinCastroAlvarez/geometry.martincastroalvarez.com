/** User - matches session API response */
export interface ApiUser {
    email: string | null;
    name: string | null;
    avatarUrl: string | null;
}

/** Job - matches geometry API job response */
export interface ApiJob {
    id: string;
    parent_id: string | null;
    children_ids: string[];
    status: string;
    stage: string;
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
    owner_email: string;
    owner_job_id: string;
    title?: string;
    ears?: Record<string, unknown>;
    convex_components?: Record<string, unknown>;
    guards?: Record<string, ApiPoint>;
    visibility?: Record<string, ApiPoint[]>;
    created_at: string;
    updated_at: string;
}

export interface PageResponse<T> {
    records: T[];
    next_token: string;
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
    stage: string;
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
    owner_email: string;
    owner_job_id: string;
    title: string;
    ears?: Record<string, unknown>;
    convex_components?: Record<string, unknown>;
    guards?: Record<string, unknown>;
    visibility?: Record<string, unknown>;
    created_at: string;
    updated_at: string;
}
