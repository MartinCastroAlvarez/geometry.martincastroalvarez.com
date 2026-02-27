/**
 * React Query hooks for art galleries (list and single, domain Gallery with ArtGallery).
 *
 * Context: Fetches from Geometry API /v1/galleries, normalizes with fromApiArtGallery +
 * toDomainArtGallery so components receive Gallery (id, title, artGallery: ArtGallery).
 * Query keys and stale times from constants.ts (GALLERIES_QUERY_KEY, GALLERY_QUERY_KEY, STALE_TIME_*).
 * List supports pagination via nextToken/limit; single gallery is cached per id.
 *
 * Example:
 *   const { data } = useArtGalleries({ limit: 10 });
 *   const { data: gallery } = useArtGallery(galleryId);  // gallery.artGallery is ArtGallery
 */

import { useQuery } from "@tanstack/react-query";
import { geometryApiClient } from "./geometry";
import { fromApiArtGallery, toDomainArtGallery } from "./adapters";
import {
    GALLERIES_QUERY_KEY,
    GALLERY_QUERY_KEY,
    STALE_TIME_GALLERIES_LIST_MS,
    STALE_TIME_GALLERY_MS,
} from "./constants";

export { GALLERIES_QUERY_KEY, GALLERY_QUERY_KEY } from "./constants";

export const useArtGalleries = (params?: { nextToken?: string; limit?: number }) => {
    return useQuery({
        queryKey: [...GALLERIES_QUERY_KEY, params?.nextToken ?? "", params?.limit ?? 20],
        queryFn: async () => {
            const data = await geometryApiClient.getArtGalleries(params);
            return {
                records: data.records.map((r) => toDomainArtGallery(fromApiArtGallery(r))),
                next_token: data.next_token,
            };
        },
        staleTime: STALE_TIME_GALLERIES_LIST_MS,
    });
};

export const useArtGallery = (galleryId: string | null) => {
    return useQuery({
        queryKey: GALLERY_QUERY_KEY(galleryId ?? ""),
        queryFn: async () => {
            if (!galleryId) throw new Error("galleryId required");
            const data = await geometryApiClient.getArtGallery(galleryId);
            return toDomainArtGallery(fromApiArtGallery(data));
        },
        enabled: !!galleryId,
        staleTime: STALE_TIME_GALLERY_MS,
    });
};
