/**
 * Geometry API client: jobs and art galleries (CRUD, publish).
 *
 * Context: Constructor accepts optional jwtToken. When set, protected methods (getJobs,
 * getJob, publish, updateJob, createJob) send it in X-Auth and throw if token
 * is null/undefined. getArtGalleries and getArtGallery do not require token (public).
 * No interceptor; token is passed explicitly. Used by job.ts and gallery.ts hooks.
 *
 * Example:
 *   const client = new GeometryApiClient(GEOMETRY_API_URL, token);
 *   const jobs = await client.getJobs({ limit: 10 });
 */

import { parseSummaryFromApi, type Summary } from "@geometry/domain";
import { GEOMETRY_API_URL } from "./constants";
import { toJobPayloadWire, toPolygonPayloadWire } from "./adapters";
import type {
    ApiErrorResponse,
    ListResponse,
    DetailsResponse,
    GeometryApiJob,
    GeometryApiArtGallery,
} from "./types";

export type {
    ListResponse,
    DetailsResponse,
    GeometryApiJob,
    GeometryApiArtGallery,
} from "./types";
export type { Summary } from "@geometry/domain";

const request = (
    url: string,
    jwtToken: string | null | undefined,
    options: RequestInit = {},
): Promise<Response> => {
    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    if (jwtToken) headers.set("X-Auth", jwtToken);
    return fetch(url, { ...options, headers });
};

const requestOrThrow = async (
    url: string,
    jwtToken: string | null | undefined,
    options: RequestInit = {},
): Promise<Response> => {
    const response = await request(url, jwtToken, options);
    if (!response.ok) {
        if (response.status === 503) {
            throw new Error("SERVICE_UNAVAILABLE");
        }
        let message = `${response.status} ${response.statusText}`;
        let apiError: ApiErrorResponse["error"] | undefined;
        try {
            const body = (await response.json()) as ApiErrorResponse | { error?: { message?: string } };
            if (body?.error?.message) message = body.error.message;
            if (body?.error && "type" in body.error && "code" in body.error) {
                apiError = body.error as ApiErrorResponse["error"];
            }
        } catch {
            // ignore JSON parse failure, use status text
        }
        const err = new Error(message) as Error & { apiError?: ApiErrorResponse["error"] };
        err.apiError = apiError;
        throw err;
    }
    return response;
};

const requireToken = (method: string): void => {
    throw new Error(`JWT required for ${method}`);
};

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

    async updateJob(jobId: string, meta: Record<string, string>): Promise<GeometryApiJob> {
        if (this.jwtToken == null || this.jwtToken === "") requireToken("updateJob");
        const response = await requestOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`, this.jwtToken, {
            method: "PATCH",
            body: JSON.stringify({ meta }),
        });
        return response.json();
    }

    async deleteJob(jobId: string): Promise<void> {
        if (this.jwtToken == null || this.jwtToken === "") requireToken("deleteJob");
        await requestOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`, this.jwtToken, {
            method: "DELETE",
        });
    }

    async createJob(
        boundary: Array<{ x: number; y: number }>,
        obstacles: Array<Array<{ x: number; y: number }>>,
        title?: string,
    ): Promise<GeometryApiJob> {
        if (this.jwtToken == null || this.jwtToken === "") requireToken("createJob");
        const body = toJobPayloadWire({ boundary, obstacles }) as Record<string, unknown>;
        if (title != null && title !== "") body.title = title;
        const response = await requestOrThrow(`${this.baseUrl}/v1/jobs`, this.jwtToken, {
            method: "POST",
            body: JSON.stringify(body),
        });
        return response.json();
    }

    /**
     * Validate polygon (boundary and obstacles). Returns Summary with "status", "status.note",
     * and per-check keys (e.g. "polygon.convex", "polygon.convex.note").
     * Public endpoint; token optional (not required for validation).
     */
    async validatePolygon(
        boundary: Array<{ x: number; y: number }>,
        obstacles: Array<Array<{ x: number; y: number }>>,
    ): Promise<Summary> {
        const body = toPolygonPayloadWire({ boundary, obstacles });
        const response = await requestOrThrow(`${this.baseUrl}/v1/polygon`, this.jwtToken, {
            method: "POST",
            body: JSON.stringify(body),
        });
        const raw = (await response.json()) as Record<string, string>;
        return parseSummaryFromApi(raw);
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
