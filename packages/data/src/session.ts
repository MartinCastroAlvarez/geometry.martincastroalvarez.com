import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { User } from "@geometry/domain";
import { AUTH_REDIRECT_URL } from "./constants";
import { authApiClient } from "./auth";
import { toDomainUser } from "./adapters";

export const sessionQueryKey = ["session"] as const;

export const useSession = () => {
    return useQuery({
        queryKey: sessionQueryKey,
        queryFn: async () => {
            const data = await authApiClient.getSession();
            if (data === null) return null;
            return User.fromDict(toDomainUser(data));
        },
        staleTime: 15 * 60 * 1000, // 15 minutes - session changes infrequently
        retry: (failureCount, error) => {
            const msg = String(error);
            if (msg.includes("401") || msg.includes("403") || msg.includes("Unauthorized")) {
                return false;
            }
            return failureCount < 3;
        },
    });
};

export const useLogout = () => {
    return useCallback(() => {
        const returnUrl = encodeURIComponent(window.location.href);
        window.location.href = `${AUTH_REDIRECT_URL}?text=${returnUrl}`;
    }, []);
};
