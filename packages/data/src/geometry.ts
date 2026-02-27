import { GEOMETRY_API_URL } from "./constants";
import { fetchWithAuth } from "./cookies";
import type { PageResponse, GeometryApiJob, GeometryApiArtGallery } from "./types";

const fetchWithAuthOrThrow = async (url: string, options: RequestInit = {}): Promise<Response> => {
    const response = await fetchWithAuth(url, options);
    if (!response.ok) {
        throw new Error(`Geometry API error: ${response.status} ${response.statusText}`);
    }
    return response;
};

export type { PageResponse, GeometryApiJob, GeometryApiArtGallery } from "./types";

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
        const response = await fetchWithAuthOrThrow(url);
        return response.json();
    }

    async getJob(jobId: string): Promise<GeometryApiJob> {
        const response = await fetchWithAuthOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`);
        return response.json();
    }

    async publish(jobId: string): Promise<GeometryApiArtGallery> {
        const response = await fetchWithAuthOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`, {
            method: "POST",
        });
        return response.json();
    }

    async unpublish(jobId: string): Promise<{ deleted: boolean; id: string }> {
        const response = await fetchWithAuthOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`, {
            method: "DELETE",
        });
        return response.json();
    }

    async updateJob(jobId: string, meta: Record<string, string>): Promise<GeometryApiJob> {
        const response = await fetchWithAuthOrThrow(`${this.baseUrl}/v1/jobs/${jobId}`, {
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
        const response = await fetchWithAuthOrThrow(url);
        return response.json();
    }

    async getArtGallery(galleryId: string): Promise<GeometryApiArtGallery> {
        const response = await fetchWithAuthOrThrow(`${this.baseUrl}/v1/galleries/${galleryId}`);
        return response.json();
    }

    async createJob(boundary: Array<{ x: number; y: number }>, obstacles: Array<Array<{ x: number; y: number }>>): Promise<GeometryApiJob> {
        const response = await fetchWithAuthOrThrow(`${this.baseUrl}/v1/jobs`, {
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
