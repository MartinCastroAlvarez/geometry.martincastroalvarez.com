/**
 * Adapters between API response shapes and @geometry/domain models.
 *
 * Context: The backend returns plain JSON (ApiJob, ApiArtGallery, ApiUser). We convert
 * to domain types (Job, Gallery, User) so the rest of the app works with rich objects
 * (e.g. ArtGallery, Polygon, Point) and stays independent of API field names.
 * polygonToApiFormat converts domain Polygon to the wire format for validatePolygon and createJob.
 *
 * Example:
 *   const apiJob = await geometryApiClient.getJob(id);
 *   const job = toDomainJob(fromApiJob(apiJob));  // Job with typed meta, stdout, etc.
 *   polygonToApiFormat(domainPolygon);  // [{ x, y }, ...] for API
 */

import { ArtGallery, Point, Polygon } from "@geometry/domain";
import type { Job, Gallery } from "@geometry/domain";
import type { ApiUser, ApiJob, ApiArtGallery, ApiPolygon } from "./types";

export const toDomainUser = (api: ApiUser): { email: string | null; name: string | null; avatarUrl: string | null } => {
    return {
        email: api.email ?? null,
        name: api.name ?? null,
        avatarUrl: api.avatarUrl ?? null,
    };
};

export const toDomainJob = (api: ApiJob): Job => {
    return {
        id: api.id,
        status: api.status,
        stage: api.stage,
        meta: api.meta ?? {},
        stdout: api.stdout ?? {},
    };
};

export const toDomainArtGallery = (api: ApiArtGallery): Gallery => {
    const perimeter = new Polygon(api.boundary.points.map((p) => new Point(p.x, p.y)));
    const holes = Object.values(api.obstacles).map(
        (obs) => new Polygon((obs?.points ?? []).map((p) => new Point(p.x, p.y)))
    );
    const guards = Object.values(api.guards ?? {}).map((p) => new Point(p.x, p.y));
    const artGallery = new ArtGallery(perimeter, holes, guards);
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

/** Convert domain Polygon to API wire format (array of { x, y }) for validatePolygon and createJob. */
export const polygonToApiFormat = (poly: Polygon): Array<{ x: number; y: number }> => {
    return poly.points.map((p) => p.toDict());
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
