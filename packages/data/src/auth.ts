/**
 * Session API client: get current user from the auth service.
 *
 * Context: Single endpoint GET /v1/session. Constructor accepts optional jwtToken; when present
 * it is sent in the X-Auth header. getSession() throws if jwtToken is null/undefined (query
 * should not be sent). Returns SessionResponse (email, name, avatarUrl) or null on 401/403.
 * Used by session.ts useSession hook. No interceptor; token is passed explicitly.
 *
 * Example:
 *   const client = new AuthApiClient(SESSION_API_URL, token);
 *   const data = await client.getSession();  // SessionResponse | null
 */

import { SESSION_API_URL } from "./constants";
import type { SessionResponse } from "./types";

export type { SessionResponse } from "./types";

function fetchWithToken(url: string, jwtToken: string, options: RequestInit = {}): Promise<Response> {
    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    headers.set("X-Auth", jwtToken);
    return fetch(url, { ...options, headers });
}

export class AuthApiClient {
    private baseUrl: string;
    private jwtToken: string | null | undefined;

    constructor(baseUrl: string = SESSION_API_URL, jwtToken?: string | null) {
        this.baseUrl = baseUrl.replace(/\/$/, "");
        this.jwtToken = jwtToken;
    }

    async getSession(): Promise<SessionResponse | null> {
        if (this.jwtToken == null || this.jwtToken === "") {
            throw new Error("JWT required for getSession");
        }
        const response = await fetchWithToken(`${this.baseUrl}/v1/session`, this.jwtToken);
        if (response.status === 401 || response.status === 403) {
            return null;
        }
        if (!response.ok) {
            throw new Error(`Session API error: ${response.statusText}`);
        }
        return response.json();
    }
}
