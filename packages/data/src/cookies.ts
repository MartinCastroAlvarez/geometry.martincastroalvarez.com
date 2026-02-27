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
    const JWT_COOKIE_NAME = "jwt";
    const encodedName = encodeURIComponent(JWT_COOKIE_NAME) + "=";
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(encodedName)) {
            return decodeURIComponent(trimmed.substring(encodedName.length));
        }
    }
    const meta = import.meta as unknown as { env?: { VITE_JWT_TEST?: string } };
    return meta?.env?.VITE_JWT_TEST ?? null;
};
