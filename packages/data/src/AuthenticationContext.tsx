/**
 * Auth token context: pass JWT from app (e.g. VITE_JWT_TEST) and read it in clients.
 *
 * Context: Packages cannot read import.meta.env; the app must pass the token via
 * <AuthenticationProvider jwtToken={import.meta.env.VITE_JWT_TEST}>.
 * Clients get the token via useAuthToken() (context first, then cookie fallback).
 * fetchWithAuth / getAuthToken use the same source so API calls are authenticated.
 */
import React, { createContext, useContext, useEffect } from "react";
import { getAuthToken, setDevAuthToken } from "./cookies";

type AuthTokenContextValue = string | null;

const AuthTokenContext = createContext<AuthTokenContextValue | undefined>(undefined);

export type AuthenticationProviderProps = {
    /** Optional JWT from app env (e.g. import.meta.env.VITE_JWT_TEST). When set, used for API auth instead of cookie. */
    jwtToken?: string | null;
    children: React.ReactNode;
};

/**
 * Wraps the app (or subtree) and provides the auth token. Pass jwtToken from the app
 * so packages can use it without reading env (e.g. jwtToken={import.meta.env.VITE_JWT_TEST}).
 */
export const AuthenticationProvider = ({ jwtToken, children }: AuthenticationProviderProps) => {
    useEffect(() => {
        if (jwtToken !== undefined) setDevAuthToken(jwtToken ?? null);
        return () => {
            if (jwtToken !== undefined) setDevAuthToken(null);
        };
    }, [jwtToken]);

    return <AuthTokenContext.Provider value={jwtToken}>{children}</AuthTokenContext.Provider>;
};

/**
 * Returns the auth token: from context (if set by AuthenticationProvider) or from cookie.
 * Use this in clients that need the token; fetchWithAuth uses the same source automatically.
 */
export const useAuthToken = (): string | null => {
    const fromContext = useContext(AuthTokenContext);
    if (fromContext !== undefined) return fromContext;
    return getAuthToken();
};
