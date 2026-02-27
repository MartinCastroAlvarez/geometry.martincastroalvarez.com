import { useQuery } from "@tanstack/react-query";
import { geometryApiClient } from "./geometry";
import { fromApiArtGallery, toDomainArtGallery } from "./adapters";

export const galleriesQueryKey = ["galleries"] as const;
export const galleryQueryKey = (galleryId: string) => ["galleries", galleryId] as const;

export const useArtGalleries = (params?: { nextToken?: string; limit?: number }) => {
    return useQuery({
        queryKey: [...galleriesQueryKey, params?.nextToken ?? "", params?.limit ?? 20],
        queryFn: async () => {
            const data = await geometryApiClient.getArtGalleries(params);
            return {
                records: data.records.map((r) => toDomainArtGallery(fromApiArtGallery(r))),
                next_token: data.next_token,
            };
        },
        staleTime: 2 * 60 * 1000, // 2 minutes - gallery list changes when publish/unpublish
    });
};

export const useArtGallery = (galleryId: string | null) => {
    return useQuery({
        queryKey: galleryQueryKey(galleryId ?? ""),
        queryFn: async () => {
            if (!galleryId) throw new Error("galleryId required");
            const data = await geometryApiClient.getArtGallery(galleryId);
            return toDomainArtGallery(fromApiArtGallery(data));
        },
        enabled: !!galleryId,
        staleTime: 60 * 1000, // 1 minute - gallery content is relatively static
    });
};
