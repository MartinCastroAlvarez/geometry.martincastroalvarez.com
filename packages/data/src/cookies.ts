export function getAuthToken(): string | null {
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
}
