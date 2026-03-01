/**
 * Adapters between API response shapes and @geometry/domain models.
 *
 * Context: The backend returns plain JSON (ApiJob, ApiArtGallery, ApiUser). We convert
 * to domain types (Job, Gallery, User) so the rest of the app works with rich objects
 * (e.g. ArtGallery, Polygon, Point) and stays independent of API field names.
 * polygonToApiFormat converts domain Polygon to the wire format for validatePolygon and createJob.
 *
 * When a job has valid boundary and obstacles in its stdin (from list, getJob, or createJob
 * response), we attach an ArtGallery to the job. For simplicity, the gallery is identified
 * by the job id (i.e. we do not assign a separate gallery id; use job.id when referring to
 * the job's gallery).
 *
 * Example:
 *   const apiJob = await geometryApiClient.getJob(id);
 *   const job = toDomainJob(fromApiJob(apiJob));  // Job with typed meta, stdout, artGallery if valid stdin
 *   polygonToApiFormat(domainPolygon);  // [{ x, y }, ...] for API
 */

import { ArtGallery, Point, Polygon, parseStatus } from "@geometry/domain";
import type { Job, Gallery } from "@geometry/domain";
import type { ApiUser, ApiJob, ApiArtGallery, ApiPolygon } from "./types";

export const toDomainUser = (api: ApiUser): { email: string | null; name: string | null; avatarUrl: string | null } => {
    return {
        email: api.email ?? null,
        name: api.name ?? null,
        avatarUrl: api.avatarUrl ?? null,
    };
};

/** Normalize a point from stdin: either [x, y] or { x, y }. */
function parsePoint(p: unknown): { x: number; y: number } | null {
    if (Array.isArray(p) && p.length >= 2 && typeof p[0] === "number" && typeof p[1] === "number") {
        return { x: p[0], y: p[1] };
    }
    if (p != null && typeof p === "object" && "x" in p && "y" in p) {
        const o = p as { x: unknown; y: unknown };
        if (typeof o.x === "number" && typeof o.y === "number") return { x: o.x, y: o.y };
    }
    return null;
}

/** Parse boundary from stdin: array of points ( [x,y] or {x,y} ). Must have at least 3 points. */
function parseBoundary(stdin: Record<string, unknown>): Polygon | null {
    const raw = stdin.boundary;
    if (!Array.isArray(raw) || raw.length < 3) return null;
    const points: Point[] = [];
    for (const p of raw) {
        const pt = parsePoint(p);
        if (!pt) return null;
        points.push(new Point(pt.x, pt.y));
    }
    return new Polygon(points);
}

/** Parse obstacles from stdin: array of polygons. */
function parseObstacles(stdin: Record<string, unknown>): Polygon[] {
    const raw = stdin.obstacles;
    if (!Array.isArray(raw)) return [];
    const obstacles: Polygon[] = [];
    for (const poly of raw) {
        if (!Array.isArray(poly) || poly.length < 3) continue;
        const points: Point[] = [];
        let ok = true;
        for (const p of poly) {
            const pt = parsePoint(p);
            if (!pt) {
                ok = false;
                break;
            }
            points.push(new Point(pt.x, pt.y));
        }
        if (ok && points.length >= 3) obstacles.push(new Polygon(points));
    }
    return obstacles;
}

/**
 * Build an ArtGallery from a job's stdin when it contains valid boundary and obstacles.
 * Used when reading job list, single job, or createJob response. The gallery is conceptually
 * identified by the job id (see module doc); we do not set a separate id on ArtGallery.
 */
export function artGalleryFromJobStdin(jobId: string, stdin: Record<string, unknown>): ArtGallery | undefined {
    const boundary = parseBoundary(stdin);
    if (!boundary) return undefined;
    const obstacles = parseObstacles(stdin);
    return new ArtGallery(boundary, obstacles, []);
}

export const toDomainJob = (api: ApiJob): Job => {
    const stdin = api.stdin ?? {};
    const artGallery = artGalleryFromJobStdin(api.id, stdin);
    return {
        id: api.id,
        status: parseStatus(api.status),
        stage: api.stage,
        meta: api.meta ?? {},
        stdout: api.stdout ?? {},
        ...(artGallery != null ? { artGallery } : {}),
    };
};

export const toDomainArtGallery = (api: ApiArtGallery): Gallery => {
    const boundary = new Polygon(api.boundary.points.map((p) => new Point(p.x, p.y)));
    const obstacles = Object.values(api.obstacles).map(
        (obs) => new Polygon((obs?.points ?? []).map((p) => new Point(p.x, p.y)))
    );
    const guards = Object.values(api.guards ?? {}).map((p) => new Point(p.x, p.y));
    const artGallery = new ArtGallery(boundary, obstacles, guards);
    return {
        id: api.id,
        title: api.title,
        artGallery,
    };
};

export const fromApiJob = (raw: unknown): ApiJob => {
    const d = raw as Record<string, unknown>;
    return {
        id: String(d.id ?? ""),
        parent_id: d.parent_id != null ? String(d.parent_id) : null,
        children_ids: Array.isArray(d.children_ids) ? d.children_ids.map(String) : [],
        status: String(d.status ?? "pending"),
        stage: String(d.stage ?? "art_gallery"),
        stdin: (d.stdin as Record<string, unknown>) ?? {},
        stdout: (d.stdout as Record<string, unknown>) ?? {},
        meta: (d.meta as Record<string, unknown>) ?? {},
        stderr: (d.stderr as Record<string, unknown>) ?? {},
        created_at: String(d.created_at ?? ""),
        updated_at: String(d.updated_at ?? ""),
    };
};

/** Convert domain Polygon to API wire format (array of { x, y }) for internal use. */
export const polygonToApiFormat = (poly: Polygon): Array<{ x: number; y: number }> => {
    return poly.points.map((p) => p.toDict());
};

/** Convert a point to API wire format: list of decimals [x, y] (backend Point.unserialize expects this). */
export const pointToWireFormat = (p: { x: number; y: number }): [number, number] => [p.x, p.y];

/** Convert points array to API wire format for boundary/obstacle points. */
export const pointsToWireFormat = (points: Array<{ x: number; y: number }>): Array<[number, number]> =>
    points.map(pointToWireFormat);

/** Build the exact JSON body for validatePolygon (boundary/obstacles as { points: [...] }). */
export function toPolygonPayloadWire(payload: {
    boundary: Array<{ x: number; y: number }>;
    obstacles: Array<Array<{ x: number; y: number }>>;
}): {
    boundary: { points: Array<[number, number]> };
    obstacles: Array<{ points: Array<[number, number]> }>;
} {
    return {
        boundary: { points: pointsToWireFormat(payload.boundary) },
        obstacles: payload.obstacles.map((obs) => ({ points: pointsToWireFormat(obs) })),
    };
}

/** Build the exact JSON body for createJob (boundary as list of points; API expects boundary list, not { points }). */
export function toJobPayloadWire(payload: {
    boundary: Array<{ x: number; y: number }>;
    obstacles: Array<Array<{ x: number; y: number }>>;
}): {
    boundary: Array<[number, number]>;
    obstacles: Array<Array<[number, number]>>;
} {
    return {
        boundary: pointsToWireFormat(payload.boundary),
        obstacles: payload.obstacles.map((obs) => pointsToWireFormat(obs)),
    };
}

/** Extract boundary and obstacles from ArtGallery for validation and createJob API calls. */
export const artGalleryToValidationPayload = (artGallery: ArtGallery): {
    boundary: Array<{ x: number; y: number }>;
    obstacles: Array<Array<{ x: number; y: number }>>;
} => {
    return {
        boundary: polygonToApiFormat(artGallery.boundary),
        obstacles: artGallery.obstacles.map(polygonToApiFormat),
    };
};

export const fromApiArtGallery = (raw: unknown): ApiArtGallery => {
    const d = raw as Record<string, unknown>;
    const boundary = (d.boundary as ApiPolygon) ?? { points: [] };
    const obstacles = (d.obstacles as Record<string, ApiPolygon>) ?? {};
    const guards = (d.guards as Record<string, { x: number; y: number }>) ?? {};
    return {
        id: String(d.id ?? ""),
        boundary: Array.isArray(boundary.points) ? boundary : { points: [] },
        obstacles: typeof obstacles === "object" ? obstacles : {},
        owner_email: String(d.owner_email ?? ""),
        owner_job_id: String(d.owner_job_id ?? ""),
        title: d.title != null ? String(d.title) : undefined,
        ears: (d.ears as Record<string, unknown>) ?? {},
        convex_components: (d.convex_components as Record<string, unknown>) ?? {},
        guards,
        visibility: (d.visibility as Record<string, { x: number; y: number }[]>) ?? {},
        created_at: String(d.created_at ?? ""),
        updated_at: String(d.updated_at ?? ""),
    };
};
