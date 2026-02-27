/**
 * Session and logout hooks: current user from session API.
 *
 * Context: useSession uses useAuthentication() for the JWT, then useQuery with AuthApiClient(token).
 * When token is null/undefined the query is not sent (enabled: false). Returns { user, isLoading };
 * user is domain User or null. useLogout redirects to AUTH_REDIRECT_URL with return URL.
 *
 * Example:
 *   const { user, isLoading } = useSession();
 *   const logout = useLogout();  logout();
 */

import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { User } from "@geometry/domain";
import { AUTH_REDIRECT_URL, SESSION_API_URL, SESSION_QUERY_KEY, STALE_TIME_SESSION_MS } from "./constants";
import { AuthApiClient } from "./auth";
import { toDomainUser } from "./adapters";
import { useAuthentication } from "./useAuthToken";

export { SESSION_QUERY_KEY } from "./constants";

export const useSession = () => {
    const token = useAuthentication();
    const query = useQuery({
        queryKey: [...SESSION_QUERY_KEY, token ?? ""],
        queryFn: async () => {
            const data = await new AuthApiClient(SESSION_API_URL, token!).getSession();
            if (data === null) return null;
            return User.fromDict(toDomainUser(data));
        },
        enabled: !!token,
        staleTime: STALE_TIME_SESSION_MS,
        retry: (failureCount, error) => {
            const msg = String(error);
            if (msg.includes("401") || msg.includes("403") || msg.includes("Unauthorized")) {
                return false;
            }
            return failureCount < 3;
        },
    });
    const { data, isLoading, ...rest } = query;
    return { ...rest, user: data ?? null, isLoading };
};

export const useLogout = () => {
    return useCallback(() => {
        const returnUrl = encodeURIComponent(window.location.href);
        window.location.href = `${AUTH_REDIRECT_URL}?text=${returnUrl}`;
    }, []);
};
