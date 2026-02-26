import { useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { User } from "@geometry/domain";
import { AUTH_REDIRECT_URL } from "./constants";
import { authApiClient } from "./auth";
import { UserModel } from "./models";

export const sessionQueryKey = ["session"] as const;

export function useSession() {
    return useQuery({
        queryKey: sessionQueryKey,
        queryFn: async () => {
            const data = await authApiClient.getSession();
            if (data === null) return null;
            const apiUser = UserModel.fromApi(data);
            const domain = UserModel.toDomain(apiUser);
            return User.fromDict(domain);
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
}

export function useLogout() {
    return useCallback(() => {
        const returnUrl = encodeURIComponent(window.location.href);
        window.location.href = `${AUTH_REDIRECT_URL}?text=${returnUrl}`;
    }, []);
}
