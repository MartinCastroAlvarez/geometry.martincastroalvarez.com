import { SESSION_API_URL } from "./constants";
import { getAuthToken } from "./cookies";

async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
    const token = getAuthToken();
    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    if (token) {
        headers.set("X-Auth", token);
    }
    const response = await fetch(url, { ...options, headers });
    return response;
}

export interface SessionResponse {
    email: string | null;
    name: string | null;
    avatarUrl: string | null;
}

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
