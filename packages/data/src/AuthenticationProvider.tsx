/**
 * Authentication provider: supplies JWT from prop, cookie, or null.
 *
 * Context: Resolves token in order: (1) jwtToken prop if provided (e.g. from app env),
 * (2) "jwt" cookie via getAuthToken(), (3) null. Provides the value on AuthTokenContext so
 * useAuthentication() / useAuthToken() can pass it to API clients. No interceptor; clients
 * receive the token explicitly. Wrap the app (or subtree) that uses useAuthentication().
 *
 * Example:
 *   <AuthenticationProvider jwtToken={import.meta.env.VITE_JWT_TEST}>
 *     <App />
 *   </AuthenticationProvider>
 */

import React, { useMemo } from "react";
import { getAuthToken } from "./cookies";
import { AuthTokenContext } from "./AuthenticationContext";

export type AuthenticationProviderProps = {
    /** Optional JWT from app env. When set, overrides cookie; otherwise cookie is used. */
    jwtToken?: string | null;
    children: React.ReactNode;
};

export const AuthenticationProvider = ({ jwtToken, children }: AuthenticationProviderProps) => {
    const value = useMemo(
        () => (jwtToken !== undefined ? (jwtToken ?? null) : (getAuthToken() ?? null)),
        [jwtToken],
    );
    return <AuthTokenContext.Provider value={value}>{children}</AuthTokenContext.Provider>;
};
