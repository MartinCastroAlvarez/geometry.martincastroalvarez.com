/**
 * Geometry API client: jobs and art galleries (CRUD, publish/unpublish).
 *
 * Context: Constructor accepts optional jwtToken. When set, protected methods (getJobs,
 * getJob, publish, unpublish, updateJob, createJob) send it in X-Auth and throw if token
 * is null/undefined. getArtGalleries and getArtGallery do not require token (public).
 * No interceptor; token is passed explicitly. Used by job.ts and gallery.ts hooks.
 *
 * Example:
 *   const client = new GeometryApiClient(GEOMETRY_API_URL, token);
 *   const jobs = await client.getJobs({ limit: 10 });
 */

import { GEOMETRY_API_URL } from "./constants";
import type {
    ListResponse,
    DetailsResponse,
    GeometryApiJob,
    GeometryApiArtGallery,
    PolygonValidationResponse,
} from "./types";

export type {
    ListResponse,
    DetailsResponse,
    GeometryApiJob,
    GeometryApiArtGallery,
    PolygonValidationResponse,
} from "./types";

function request(
    url: string,
    jwtToken: string | null | undefined,
    options: RequestInit = {},
): Promise<Response> {
    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    if (jwtToken) headers.set("X-Auth", jwtToken);
    return fetch(url, { ...options, headers });
}

async function requestOrThrow(
    url: string,
    jwtToken: string | null | undefined,
    options: RequestInit = {},
): Promise<Response> {
    const response = await request(url, jwtToken, options);
    if (!response.ok) {
        throw new Error(`Geometry API error: ${response.status} ${response.statusText}`);
    }
    return response;
}

function requireToken(method: string): void {
    throw new Error(`JWT required for ${method}`);
}

export class GeometryApiClient {
    private baseUrl: string;
    private jwtToken: string | null | undefined;

    constructor(baseUrl: string = GEOMETRY_API_URL, jwtToken?: string | null) {
        this.baseUrl = baseUrl.replace(/\/$/, "");
        this.jwtToken = jwtToken;
    }

    async getJobs(params?: { nextToken?: string; limit?: number }): Promise<ListResponse<GeometryApiJob>> {
        if (this.jwtToken == null || this.jwtToken === "") requireToken("getJobs");
        const searchParams = new URLSearchParams();
        if (params?.nextToken) searchParams.set("next_token", params.nextToken);
        if (params?.limit != null) searchParams.set("limit", String(params.limit));
        const qs = searchParams.toString();
        const url = `${this.baseUrl}/v1/jobs${qs ? `?${qs}` : ""}`;
        const response = await requestOrThrow(url, this.jwtToken);
        return response.json();
    }

    async getJob(jobId: string): Promise<GeometryApiJob> {
        if (this.jwtToken == null || this.jwtToken === "") requireToken("getJob");
        const response = await requestOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`, this.jwtToken);
        const json = (await response.json()) as DetailsResponse<GeometryApiJob>;
        return json.data;
    }

    async publish(jobId: string): Promise<GeometryApiArtGallery> {
        if (this.jwtToken == null || this.jwtToken === "") requireToken("publish");
        const response = await requestOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`, this.jwtToken, {
            method: "POST",
        });
        return response.json();
    }

    async unpublish(jobId: string): Promise<{ deleted: boolean; id: string }> {
        if (this.jwtToken == null || this.jwtToken === "") requireToken("unpublish");
        const response = await requestOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`, this.jwtToken, {
            method: "DELETE",
        });
        return response.json();
    }

    async updateJob(jobId: string, meta: Record<string, string>): Promise<GeometryApiJob> {
        if (this.jwtToken == null || this.jwtToken === "") requireToken("updateJob");
        const response = await requestOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`, this.jwtToken, {
            method: "PATCH",
            body: JSON.stringify({ meta }),
        });
        return response.json();
    }

    async createJob(
        boundary: Array<{ x: number; y: number }>,
        obstacles: Array<Array<{ x: number; y: number }>>,
    ): Promise<GeometryApiJob> {
        if (this.jwtToken == null || this.jwtToken === "") requireToken("createJob");
        const response = await requestOrThrow(`${this.baseUrl}/v1/jobs`, this.jwtToken, {
            method: "POST",
            body: JSON.stringify({
                boundary: { points: boundary },
                obstacles: obstacles.map((obs) => ({ points: obs })),
            }),
        });
        return response.json();
    }

    /**
     * Validate polygon (boundary and obstacles). Returns a dict of status and note keys
     * (e.g. "polygon.convex", "polygon.convex.note", "obstacles.0.contained").
     * Public endpoint; token optional (not required for validation).
     */
    async validatePolygon(
        boundary: Array<{ x: number; y: number }>,
        obstacles: Array<Array<{ x: number; y: number }>>,
    ): Promise<PolygonValidationResponse> {
        const response = await requestOrThrow(`${this.baseUrl}/v1/polygon`, this.jwtToken, {
            method: "POST",
            body: JSON.stringify({
                boundary: { points: boundary },
                obstacles: obstacles.map((obs) => ({ points: obs })),
            }),
        });
        return response.json();
    }

    async getArtGalleries(params?: { nextToken?: string; limit?: number }): Promise<ListResponse<GeometryApiArtGallery>> {
        const searchParams = new URLSearchParams();
        if (params?.nextToken) searchParams.set("next_token", params.nextToken);
        if (params?.limit != null) searchParams.set("limit", String(params.limit));
        const qs = searchParams.toString();
        const url = `${this.baseUrl}/v1/galleries${qs ? `?${qs}` : ""}`;
        const response = await requestOrThrow(url, this.jwtToken);
        return response.json();
    }

    async getArtGallery(galleryId: string): Promise<GeometryApiArtGallery> {
        const response = await requestOrThrow(`${this.baseUrl}/v1/galleries/${galleryId}`, this.jwtToken);
        const json = (await response.json()) as DetailsResponse<GeometryApiArtGallery>;
        return json.data;
    }
}
