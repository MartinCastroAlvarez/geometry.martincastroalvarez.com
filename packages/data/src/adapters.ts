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

import { ArtGallery, ConvexComponent, Ear, Point, Polygon, Visibility, parseStatus } from "@geometry/domain";
import type { ArtGalleryDict, Gallery, Job } from "@geometry/domain";
import type { ApiUser, ApiJob, ApiArtGallery, ApiPolygon } from "./types";

export const toDomainUser = (api: ApiUser): { email: string | null; name: string | null; avatarUrl: string | null } => {
    return {
        email: api.email ?? null,
        name: api.name ?? null,
        avatarUrl: api.avatarUrl ?? null,
    };
};

/** Coerce a value to number if it's a numeric string or number; otherwise NaN. */
function toNumber(v: unknown): number {
    if (typeof v === "number" && !Number.isNaN(v)) return v;
    if (typeof v === "string") {
        const n = Number(v);
        return Number.isNaN(n) ? Number.NaN : n;
    }
    return Number.NaN;
}

/** Normalize a point from stdin: either [x, y] or { x, y }; coordinates may be numbers or numeric strings. */
function parsePoint(p: unknown): { x: number; y: number } | null {
    if (Array.isArray(p) && p.length >= 2) {
        const x = toNumber(p[0]);
        const y = toNumber(p[1]);
        if (!Number.isNaN(x) && !Number.isNaN(y)) return { x, y };
    }
    if (p != null && typeof p === "object" && "x" in p && "y" in p) {
        const o = p as { x: unknown; y: unknown };
        const x = toNumber(o.x);
        const y = toNumber(o.y);
        if (!Number.isNaN(x) && !Number.isNaN(y)) return { x, y };
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

/** Parse guards from stdout: array of points or dict (table.serialize()) with serialized points. */
function parseGuards(data: Record<string, unknown>): Point[] {
    const raw = data.guards;
    const items = Array.isArray(raw) ? raw : raw && typeof raw === "object" ? Object.values(raw) : [];
    const guards: Point[] = [];
    for (const item of items) {
        let pt: { x: number; y: number } | null = parsePoint(item);
        if (!pt && typeof item === "string") {
            try {
                const arr = JSON.parse(item) as unknown;
                if (Array.isArray(arr) && arr.length >= 2) pt = parsePoint(arr);
            } catch {
                // ignore
            }
        }
        if (pt) guards.push(new Point(pt.x, pt.y));
    }
    return guards;
}

/** Parse ears from stdout: array of 3-point polygons or dict (table.serialize()). */
function parseEars(data: Record<string, unknown>): Ear[] {
    const raw = data.ears;
    const items = Array.isArray(raw) ? raw : raw && typeof raw === "object" ? Object.values(raw) : [];
    const ears: Ear[] = [];
    for (const ear of items) {
        if (!Array.isArray(ear) || ear.length !== 3) continue;
        const points: Point[] = [];
        let ok = true;
        for (const point of ear) {
            const pt = parsePoint(point);
            if (!pt) {
                ok = false;
                break;
            }
            points.push(new Point(pt.x, pt.y));
        }
        if (ok && points.length === 3) ears.push(new Ear(points));
    }
    return ears;
}

/** Parse convex_components from stdout: array of polygons (3+ points) or dict (table.serialize()). */
function parseConvexComponents(data: Record<string, unknown>): ConvexComponent[] {
    const raw = data.convex_components;
    const items = Array.isArray(raw) ? raw : raw && typeof raw === "object" ? Object.values(raw) : [];
    const components: ConvexComponent[] = [];
    for (const poly of items) {
        if (!Array.isArray(poly) || poly.length < 3) continue;
        const points: Point[] = [];
        let ok = true;
        for (const point of poly) {
            const pt = parsePoint(point);
            if (!pt) {
                ok = false;
                break;
            }
            points.push(new Point(pt.x, pt.y));
        }
        if (ok && points.length >= 3) {
            try {
                components.push(new ConvexComponent(points));
            } catch {
                // skip invalid convex
            }
        }
    }
    return components;
}

function parsePath(path: unknown): Point[] {
    if (!Array.isArray(path)) return [];
    const points: Point[] = [];
    for (const point of path) {
        let pt: { x: number; y: number } | null = parsePoint(point);
        if (!pt && typeof point === "string") {
            try {
                const arr = JSON.parse(point) as unknown;
                if (Array.isArray(arr) && arr.length >= 2) pt = parsePoint(arr);
            } catch {
                // ignore
            }
        }
        if (pt) points.push(new Point(pt.x, pt.y));
    }
    return points;
}

/** True if value looks like an array of IDs (numbers or numeric strings) rather than points. */
function isIdList(path: unknown): boolean {
    return Array.isArray(path) && path.length > 0 && path.every((v) => typeof v === "number" || (typeof v === "string" && !Number.isNaN(Number(v))));
}

/** Parse guards and visibility from stdout; returns guards list and Visibility[] (dicts share keys).
 * API may send visibility as guard_id -> array of [x,y] points (visible region) or array of vertex/guard IDs (numeric); ID list is treated as empty path. */
function parseGuardsAndVisibility(data: Record<string, unknown>): { guards: Point[]; visibility: Visibility[] } {
    const rawGuards = data.guards;
    const rawVis = data.visibility;
    if (rawGuards != null && typeof rawGuards === "object" && !Array.isArray(rawGuards) && rawVis != null && typeof rawVis === "object" && !Array.isArray(rawVis)) {
        const keys = Object.keys(rawGuards);
        const guards: Point[] = [];
        const visibility: Visibility[] = [];
        for (const k of keys) {
            const g = parsePoint((rawGuards as Record<string, unknown>)[k]);
            const path = (rawVis as Record<string, unknown>)[k];
            if (!g) continue;
            guards.push(new Point(g.x, g.y));
            if (Array.isArray(path)) {
                const points = isIdList(path) ? [] : parsePath(path);
                visibility.push(new Visibility(new Point(g.x, g.y), points));
            }
        }
        return { guards, visibility };
    }
    const guards = parseGuards(data);
    const visItems = Array.isArray(rawVis) ? rawVis : rawVis && typeof rawVis === "object" ? Object.values(rawVis) : [];
    const visibility = visItems.map((path: unknown, i: number) => {
        const points = Array.isArray(path) && isIdList(path) ? [] : parsePath(path);
        return new Visibility(guards[i] ?? new Point(0, 0), points);
    }).filter((_, i) => guards[i] != null);
    return { guards, visibility };
}

/**
 * Build an ArtGallery from a record (stdin or stdout) when it contains valid boundary and obstacles.
 * Used when reading job list, single job, or createJob response. Optional stitched from stdout
 * (key "stitched" or "stiteched"). Parses ears, convex_components, guards, visibility when present.
 * API may send boundary/obstacles/points as [x,y] with numeric or string coordinates.
 */
export function artGalleryFromPolygonData(_jobId: string, data: Record<string, unknown>): ArtGallery | undefined {
    const boundary = parseBoundary(data);
    if (!boundary) return undefined;
    const obstacles = parseObstacles(data);
    const rawStitched = data.stitched ?? data.stiteched;
    let stitched: Polygon | undefined;
    if (Array.isArray(rawStitched) && rawStitched.length >= 2) {
        const points: Point[] = [];
        for (const p of rawStitched) {
            const pt = parsePoint(p);
            if (!pt) break;
            points.push(new Point(pt.x, pt.y));
        }
        if (points.length >= 2) stitched = new Polygon(points);
    }
    const rawStitches = data.stitches;
    const stitches: [Point, Point][] = Array.isArray(rawStitches)
        ? rawStitches
              .map((seg: unknown) => {
                  if (!Array.isArray(seg) || seg.length < 2) return null;
                  const p0 = parsePoint(seg[0]);
                  const p1 = parsePoint(seg[1]);
                  if (!p0 || !p1) return null;
                  return [new Point(p0.x, p0.y), new Point(p1.x, p1.y)] as [Point, Point];
              })
              .filter((x): x is [Point, Point] => x != null)
        : [];
    const { guards, visibility } = parseGuardsAndVisibility(data);
    const ears = parseEars(data);
    const convex_components = parseConvexComponents(data);
    return new ArtGallery(boundary, obstacles, guards, stitched, stitches, ears, convex_components, visibility);
}

export const toDomainJob = (api: ApiJob): Job => {
    const stdin = api.stdin ?? {};
    const stdout = api.stdout ?? {};
    const hasStdout = Object.keys(stdout).length > 0;
    const artGallery =
        (hasStdout ? artGalleryFromPolygonData(api.id, stdout) : undefined) ??
        artGalleryFromPolygonData(api.id, stdin);
    return {
        id: api.id,
        status: parseStatus(api.status),
        step_name: api.step_name,
        meta: api.meta ?? {},
        stdin: api.stdin ?? {},
        stdout: api.stdout ?? {},
        stderr: api.stderr ?? {},
        created_at: api.created_at ?? undefined,
        updated_at: api.updated_at ?? undefined,
        children_ids: api.children_ids ?? [],
        ...(artGallery != null ? { artGallery } : {}),
    };
};

export const toDomainArtGallery = (api: ApiArtGallery): Gallery => {
    const artGallery = ArtGallery.fromDict({
        boundary: api.boundary,
        obstacles: Object.values(api.obstacles),
        guards: Object.values(api.guards ?? {}),
        ...(api.stitched != null && { stitched: api.stitched as { points: Array<{ x: number; y: number }> } }),
        ...(api.ears != null && { ears: api.ears as ArtGalleryDict['ears'] }),
        ...(api.convex_components != null && { convex_components: api.convex_components as ArtGalleryDict['convex_components'] }),
        ...(api.visibility != null && { visibility: Object.values(api.visibility) }),
        ...(api.stitches != null && { stitches: api.stitches as ArtGalleryDict["stitches"] }),
    });
    return {
        id: api.id,
        title: api.title,
        updated_at: api.updated_at,
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
        step_name: String(d.step_name ?? d.stage ?? "art_gallery"),
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

/** Extract boundary and obstacles from ArtGallery for validation and createJob API calls.
 * Boundary is normalized to CCW and each obstacle to CW so backend convexity/ordering checks pass. */
export const artGalleryToValidationPayload = (artGallery: ArtGallery): {
    boundary: Array<{ x: number; y: number }>;
    obstacles: Array<Array<{ x: number; y: number }>>;
} => {
    return {
        boundary: polygonToApiFormat(artGallery.boundary.toCCW()),
        obstacles: artGallery.obstacles.map((poly) => polygonToApiFormat(poly.toCW())),
    };
};

export const fromApiArtGallery = (raw: unknown): ApiArtGallery => {
    const d = raw as Record<string, unknown>;
    const boundary = (d.boundary as ApiPolygon) ?? { points: [] };
    const obstacles = (d.obstacles as Record<string, ApiPolygon>) ?? {};
    const guards = (d.guards as Record<string, { x: number; y: number }>) ?? {};
    const stitchedRaw = d.stitched ?? d.stiteched ?? null;
    return {
        id: String(d.id ?? ""),
        boundary: Array.isArray(boundary.points) ? boundary : { points: [] },
        obstacles: typeof obstacles === "object" ? obstacles : {},
        owner_job_id: String(d.owner_job_id ?? ""),
        title: d.title != null ? String(d.title) : undefined,
        ears: (d.ears as Record<string, unknown>) ?? {},
        convex_components: (d.convex_components as Record<string, unknown>) ?? {},
        guards,
        visibility: (d.visibility as Record<string, { x: number; y: number }[]>) ?? {},
        stitched: stitchedRaw != null ? (stitchedRaw as ApiArtGallery["stitched"]) : undefined,
        stitches: (d.stitches as ApiArtGallery["stitches"]) ?? undefined,
        created_at: String(d.created_at ?? ""),
        updated_at: String(d.updated_at ?? ""),
    };
};
