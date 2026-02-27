/**
 * Session and logout hooks: current user and redirect-to-login.
 *
 * Context: useSession fetches /v1/session via auth API, returns User (domain) or null.
 * Query key and stale time from constants.ts (SESSION_QUERY_KEY, STALE_TIME_SESSION_MS). Uses getAuthToken (env or cookie);
 * 401/403 are treated as "no session" and not retried. useLogout redirects to
 * AUTH_REDIRECT_URL with return URL for post-login redirect.
 *
 * Example:
 *   const { user } = useSession();  // User | null
 *   const logout = useLogout();  logout();  // redirect to login with returnUrl
 */

import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { User } from "@geometry/domain";
import { AUTH_REDIRECT_URL, SESSION_QUERY_KEY, STALE_TIME_SESSION_MS } from "./constants";
import { authApiClient } from "./auth";
import { toDomainUser } from "./adapters";

export { SESSION_QUERY_KEY } from "./constants";

export const useSession = () => {
    const query = useQuery({
        queryKey: SESSION_QUERY_KEY,
        queryFn: async () => {
            const data = await authApiClient.getSession();
            if (data === null) return null;
            return User.fromDict(toDomainUser(data));
        },
        staleTime: STALE_TIME_SESSION_MS,
        // Do not retry on 401/403 or "Unauthorized": these mean the token is missing, expired, or
        // insufficient. Retrying would not fix the result (user must log in) and would delay
        // showing the logged-out state and add pointless load on the session API.
        retry: (failureCount, error) => {
            const msg = String(error);
            if (msg.includes("401") || msg.includes("403") || msg.includes("Unauthorized")) {
                return false;
            }
            return failureCount < 3;
        },
    });
    const { data, isLoading, ...rest } = query;
    return { ...rest, user: data, isLoading };
};

export const useLogout = () => {
    return useCallback(() => {
        const returnUrl = encodeURIComponent(window.location.href);
        window.location.href = `${AUTH_REDIRECT_URL}?text=${returnUrl}`;
    }, []);
};
