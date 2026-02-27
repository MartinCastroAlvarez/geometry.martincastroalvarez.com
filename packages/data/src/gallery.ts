/**
 * React Query hooks for art galleries (list and single).
 *
 * Context: Uses useAuthentication() for JWT and passes it to GeometryApiClient. getArtGalleries
 * and getArtGallery do not require token (public); token is passed when available. Returns
 * galleries/gallery and isLoading. Query keys and stale times from constants.ts.
 *
 * Example:
 *   const { galleries, isLoading } = useArtGalleries({ limit: 10 });
 *   const { gallery, isLoading } = useArtGallery(galleryId);
 */

import { useQuery } from "@tanstack/react-query";
import { GeometryApiClient } from "./geometry";
import { fromApiArtGallery, toDomainArtGallery } from "./adapters";
import {
    GEOMETRY_API_URL,
    GALLERIES_QUERY_KEY,
    GALLERY_QUERY_KEY,
    STALE_TIME_GALLERIES_LIST_MS,
    STALE_TIME_GALLERY_MS,
} from "./constants";
import { useAuthentication } from "./useAuthToken";

export { GALLERIES_QUERY_KEY, GALLERY_QUERY_KEY } from "./constants";

export const useArtGalleries = (params?: { nextToken?: string; limit?: number }) => {
    const token = useAuthentication();
    const query = useQuery({
        queryKey: [...GALLERIES_QUERY_KEY, params?.nextToken ?? "", params?.limit ?? 20],
        queryFn: async () => {
            const data = await new GeometryApiClient(GEOMETRY_API_URL, token).getArtGalleries(params);
            return {
                records: data.records.map((r) => toDomainArtGallery(fromApiArtGallery(r))),
                next_token: data.next_token,
            };
        },
        staleTime: STALE_TIME_GALLERIES_LIST_MS,
    });
    const { data, isLoading, ...rest } = query;
    return { ...rest, galleries: data, isLoading };
};

export const useArtGallery = (galleryId: string | null) => {
    const token = useAuthentication();
    const query = useQuery({
        queryKey: GALLERY_QUERY_KEY(galleryId ?? ""),
        queryFn: async () => {
            if (!galleryId) throw new Error("galleryId required");
            const data = await new GeometryApiClient(GEOMETRY_API_URL, token).getArtGallery(galleryId);
            return toDomainArtGallery(fromApiArtGallery(data));
        },
        enabled: !!galleryId,
        staleTime: STALE_TIME_GALLERY_MS,
    });
    const { data, isLoading, ...rest } = query;
    return { ...rest, gallery: data, isLoading };
};
