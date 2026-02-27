/**
 * useAuthToken / useAuthentication hook: read JWT from authentication context.
 *
 * Context: Returns the token from AuthTokenContext (supplied by AuthenticationProvider).
 * The provider resolves token from prop or cookie or null. Use this in session/job/gallery
 * hooks to pass the token to API clients. Falls back to getAuthToken() (cookie) when used
 * outside the provider.
 *
 * Example:
 *   const token = useAuthentication();
 *   if (token) { const client = new AuthApiClient(url, token); ... }
 */

import { useContext } from "react";
import { AuthTokenContext } from "./AuthenticationContext";
import { getAuthToken } from "./cookies";

export const useAuthToken = (): string | null => {
    const fromContext = useContext(AuthTokenContext);
    if (fromContext !== undefined) return fromContext;
    return getAuthToken();
};

/** Alias for useAuthToken; use when you need the JWT for API clients. */
export const useAuthentication = useAuthToken;
