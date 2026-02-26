import { GEOMETRY_API_URL } from "./constants";
import { getAuthToken } from "./cookies";

async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
    const token = getAuthToken();
    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    if (token) {
        headers.set("X-Auth", token);
    }
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
        throw new Error(`Geometry API error: ${response.status} ${response.statusText}`);
    }
    return response;
}

export interface PageResponse<T> {
    records: T[];
    next_token: string;
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

export class GeometryApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = GEOMETRY_API_URL) {
        this.baseUrl = baseUrl.replace(/\/$/, "");
    }

    async getJobs(params?: { nextToken?: string; limit?: number }): Promise<PageResponse<GeometryApiJob>> {
        const searchParams = new URLSearchParams();
        if (params?.nextToken) searchParams.set("next_token", params.nextToken);
        if (params?.limit != null) searchParams.set("limit", String(params.limit));
        const qs = searchParams.toString();
        const url = `${this.baseUrl}/v1/jobs${qs ? `?${qs}` : ""}`;
        const response = await fetchWithAuth(url);
        return response.json();
    }

    async getJob(jobId: string): Promise<GeometryApiJob> {
        const response = await fetchWithAuth(`${this.baseUrl}/v1/jobs/${jobId}`);
        return response.json();
    }

    async publish(jobId: string): Promise<GeometryApiArtGallery> {
        const response = await fetchWithAuth(`${this.baseUrl}/v1/jobs/${jobId}`, {
            method: "POST",
        });
        return response.json();
    }

    async unpublish(jobId: string): Promise<{ deleted: boolean; id: string }> {
        const response = await fetchWithAuth(`${this.baseUrl}/v1/jobs/${jobId}`, {
            method: "DELETE",
        });
        return response.json();
    }

    async updateJob(jobId: string, meta: Record<string, string>): Promise<GeometryApiJob> {
        const response = await fetchWithAuth(`${this.baseUrl}/v1/jobs/${jobId}`, {
            method: "PATCH",
            body: JSON.stringify({ meta }),
        });
        return response.json();
    }

    async getArtGalleries(params?: { nextToken?: string; limit?: number }): Promise<PageResponse<GeometryApiArtGallery>> {
        const searchParams = new URLSearchParams();
        if (params?.nextToken) searchParams.set("next_token", params.nextToken);
        if (params?.limit != null) searchParams.set("limit", String(params.limit));
        const qs = searchParams.toString();
        const url = `${this.baseUrl}/v1/galleries${qs ? `?${qs}` : ""}`;
        const response = await fetchWithAuth(url);
        return response.json();
    }

    async getArtGallery(galleryId: string): Promise<GeometryApiArtGallery> {
        const response = await fetchWithAuth(`${this.baseUrl}/v1/galleries/${galleryId}`);
        return response.json();
    }

    async createJob(boundary: Array<{ x: number; y: number }>, obstacles: Array<Array<{ x: number; y: number }>>): Promise<GeometryApiJob> {
        const response = await fetchWithAuth(`${this.baseUrl}/v1/jobs`, {
            method: "POST",
            body: JSON.stringify({
                boundary: { points: boundary },
                obstacles: obstacles.map((obs) => ({ points: obs })),
            }),
        });
        return response.json();
    }
}

export const geometryApiClient = new GeometryApiClient();
