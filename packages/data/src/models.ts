import { ArtGallery as DomainArtGallery, Point, Polygon } from "@geometry/domain";

/** User model - matches session API response */
export interface ApiUser {
    email: string | null;
    name: string | null;
    avatarUrl: string | null;
}

export class UserModel {
    static fromApi(data: ApiUser): ApiUser {
        return {
            email: data.email ?? null,
            name: data.name ?? null,
            avatarUrl: data.avatarUrl ?? null,
        };
    }

    static toDomain(data: ApiUser): { email: string | null; name: string | null; avatarUrl: string | null } {
        return {
            email: data.email ?? null,
            name: data.name ?? null,
            avatarUrl: data.avatarUrl ?? null,
        };
    }

    static fromDomain(domain: { email?: string | null; name?: string | null; avatarUrl?: string | null }): ApiUser {
        return {
            email: domain.email ?? null,
            name: domain.name ?? null,
            avatarUrl: domain.avatarUrl ?? null,
        };
    }
}

/** Job model - matches geometry API job response */
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

export class JobModel {
    static fromApi(data: unknown): ApiJob {
        const d = data as Record<string, unknown>;
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
    }

    static toDomain(data: ApiJob): { id: string; status: string; stage: string; stdout: Record<string, unknown> } {
        return {
            id: data.id,
            status: data.status,
            stage: data.stage,
            stdout: data.stdout,
        };
    }

    static fromDomain(domain: { boundary?: unknown; obstacles?: unknown }): { boundary: unknown; obstacles: unknown } {
        return {
            boundary: domain.boundary ?? { points: [] },
            obstacles: domain.obstacles ?? [],
        };
    }
}

/** ArtGallery model - matches geometry API gallery response */
export interface ApiPoint {
    x: number;
    y: number;
}

export interface ApiPolygon {
    points: ApiPoint[];
}

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

export class ArtGalleryModel {
    static fromApi(data: unknown): ApiArtGallery {
        const d = data as Record<string, unknown>;
        const boundary = (d.boundary as ApiPolygon) ?? { points: [] };
        const obstacles = (d.obstacles as Record<string, ApiPolygon>) ?? {};
        const guards = (d.guards as Record<string, ApiPoint>) ?? {};
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
            visibility: (d.visibility as Record<string, ApiPoint[]>) ?? {},
            created_at: String(d.created_at ?? ""),
            updated_at: String(d.updated_at ?? ""),
        };
    }

    static toDomain(data: ApiArtGallery): DomainArtGallery {
        const perimeter = new Polygon(data.boundary.points.map((p) => new Point(p.x, p.y)));
        const holes = Object.values(data.obstacles).map(
            (obs) => new Polygon((obs.points ?? []).map((p) => new Point(p.x, p.y))),
        );
        const guards = Object.values(data.guards ?? {}).map((p) => new Point(p.x, p.y));
        return new DomainArtGallery(perimeter, holes, guards);
    }

    static fromDomain(domain: DomainArtGallery): { boundary: ApiPolygon; obstacles: ApiPolygon[] } {
        return {
            boundary: { points: domain.perimeter.points.map((p) => ({ x: p.x, y: p.y })) },
            obstacles: domain.holes.map((h) => ({ points: h.points.map((p) => ({ x: p.x, y: p.y })) })),
        };
    }
}
