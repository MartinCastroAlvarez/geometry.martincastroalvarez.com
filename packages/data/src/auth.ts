import { SESSION_API_URL } from "./constants";
import { fetchWithAuth } from "./cookies";
import type { SessionResponse } from "./types";

export type { SessionResponse } from "./types";

export class AuthApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = SESSION_API_URL) {
        this.baseUrl = baseUrl.replace(/\/$/, "");
    }

    async getSession(): Promise<SessionResponse | null> {
        const response = await fetchWithAuth(`${this.baseUrl}/v1/session`);
        if (response.status === 401 || response.status === 403) {
            return null;
        }
        if (!response.ok) {
            throw new Error(`Session API error: ${response.statusText}`);
        }
        return response.json();
    }
}

export const authApiClient = new AuthApiClient();
