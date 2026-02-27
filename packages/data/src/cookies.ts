/**
 * Auth token handling and authenticated fetch for the data layer.
 *
 * Context: All API calls (session, geometry, jobs, galleries) need a JWT. The token is
 * resolved in order: (1) VITE_JWT_TEST env (local dev via spy.sh), (2) "jwt" cookie (production).
 * This file is the single place that reads the token and attaches it to outgoing requests.
 *
 * Example:
 *   const token = getAuthToken();           // from env or cookie
 *   const res = await fetchWithAuth('/v1/jobs');  // sends X-Auth: <token>
 */

export const fetchWithAuth = async (url: string, options: RequestInit = {}): Promise<Response> => {
    const token = getAuthToken();
    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    if (token) {
        headers.set("X-Auth", token);
    }
    return fetch(url, { ...options, headers });
};

export const getAuthToken = (): string | null => {
    const meta = import.meta as unknown as { env?: { VITE_JWT_TEST?: string } };
    const fromEnv = meta?.env?.VITE_JWT_TEST;
    if (fromEnv) return fromEnv;
    const JWT_COOKIE_NAME = "jwt";
    const encodedName = encodeURIComponent(JWT_COOKIE_NAME) + "=";
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(encodedName)) {
            return decodeURIComponent(trimmed.substring(encodedName.length));
        }
    }
    return null;
};
