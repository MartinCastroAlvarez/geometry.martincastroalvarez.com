/**
 * Auth token handling and authenticated fetch for the data layer.
 *
 * Context: All API calls (session, geometry, jobs, galleries) need a JWT. The token is
 * resolved in order: (1) token from AuthenticationProvider (e.g. jwtToken={import.meta.env.VITE_JWT_TEST}),
 * (2) "jwt" cookie (production). Use <AuthenticationProvider jwtToken={...}> in the app to pass env.
 *
 * Example:
 *   <AuthenticationProvider jwtToken={import.meta.env.VITE_JWT_TEST}>...</AuthenticationProvider>
 *   const token = getAuthToken(); // or useAuthToken() in React
 *   const res = await fetchWithAuth('/v1/jobs');  // sends X-Auth: <token>
 */

let devAuthToken: string | null = null;

/** Used by AuthenticationProvider to sync jwtToken into the data layer. Not part of public API. */
export const setDevAuthToken = (token: string | null): void => {
    devAuthToken = token;
};

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
    if (devAuthToken) return devAuthToken;
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
