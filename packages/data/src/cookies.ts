/**
 * Auth token from cookie for the data layer.
 *
 * Context: getAuthToken() reads the "jwt" cookie. AuthenticationProvider resolves the token
 * from prop (if provided) or from this cookie, or null. API clients receive the token explicitly
 * (no global fetch interceptor). Use useAuthentication() in React to get the resolved token.
 *
 * Example:
 *   const token = getAuthToken();  // or useAuthentication() in React
 */

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
    return null;
};
