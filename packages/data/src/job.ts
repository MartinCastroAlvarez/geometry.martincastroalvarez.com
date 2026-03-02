/**
 * React Query hooks for jobs (list, single, publish, update, create).
 *
 * Context: Uses useAuthentication() for JWT and passes it to GeometryApiClient. Queries are
 * enabled only when token is present; mutations use the token in the client. Returns
 * jobs/job and isLoading. Query keys and stale times from constants.ts.
 *
 * Example:
 *   const { jobs, isLoading } = useJobs({ limit: 20 });
 *   const { job, isLoading } = useJob(jobId);
 *   const publish = usePublish();  publish.mutate(jobId);
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { GeometryApiClient } from "./geometry";
import { fromApiJob, toDomainJob, artGalleryToValidationPayload } from "./adapters";
import {
    GEOMETRY_API_URL,
    GALLERIES_QUERY_KEY,
    JOBS_QUERY_KEY,
    JOB_QUERY_KEY,
    JOB_CHILDREN_QUERY_KEY,
    STALE_TIME_JOBS_LIST_MS,
    STALE_TIME_JOB_MS,
} from "./constants";
import { useAuthentication } from "./useAuthToken";
import type { ArtGallery, Job } from "@geometry/domain";

export { JOBS_QUERY_KEY, JOB_QUERY_KEY, JOB_CHILDREN_QUERY_KEY } from "./constants";

/** Fetches multiple jobs by ID in parallel and returns them in the same order as the given ids. */
export async function getChildren(
    baseUrl: string,
    token: string | null | undefined,
    jobIds: string[],
): Promise<Job[]> {
    if (jobIds.length === 0) return [];
    const client = new GeometryApiClient(baseUrl, token);
    const results = await Promise.all(jobIds.map((id) => client.getJob(id)));
    return results.map((r) => toDomainJob(fromApiJob(r)));
}

export const useJobChildren = (jobIds: string[] | null | undefined) => {
    const token = useAuthentication();
    const query = useQuery({
        queryKey: [...JOB_CHILDREN_QUERY_KEY(jobIds ?? []), token ?? ""],
        queryFn: async () => {
            if (!jobIds?.length) return [];
            return getChildren(GEOMETRY_API_URL, token, jobIds);
        },
        enabled: !!token && !!jobIds?.length,
        staleTime: STALE_TIME_JOB_MS,
    });
    return { ...query, children: query.data ?? [], isLoading: query.isLoading };
};

/** Extract boundary and obstacles from an ArtGallery for validation/create API calls. */
export function validateJob(artGallery: ArtGallery): {
    boundary: Array<{ x: number; y: number }>;
    obstacles: Array<Array<{ x: number; y: number }>>;
} {
    return artGalleryToValidationPayload(artGallery);
}

export const useJobs = (params?: { nextToken?: string; limit?: number }) => {
    const token = useAuthentication();
    const query = useQuery({
        queryKey: [...JOBS_QUERY_KEY, params?.nextToken ?? "", params?.limit ?? 20, token ?? ""],
        queryFn: async () => {
            console.log("[data] useJobs request", { params, token: token ?? null });
            const res = await new GeometryApiClient(GEOMETRY_API_URL, token).getJobs(params);
            const out = {
                data: res.data.map((r) => toDomainJob(fromApiJob(r))),
                next_token: res.next_token,
            };
            console.log("[data] useJobs response", out);
            return out;
        },
        enabled: !!token,
        staleTime: STALE_TIME_JOBS_LIST_MS,
    });
    const { data, isLoading, ...rest } = query;
    return { ...rest, jobs: data, isLoading };
};

export const useJob = (jobId: string | null) => {
    const token = useAuthentication();
    const query = useQuery({
        queryKey: [...JOB_QUERY_KEY(jobId ?? ""), token ?? ""],
        queryFn: async () => {
            if (!jobId) throw new Error("jobId required");
            console.log("[data] useJob request", { jobId, token: token ?? null });
            const data = await new GeometryApiClient(GEOMETRY_API_URL, token).getJob(jobId);
            const out = toDomainJob(fromApiJob(data));
            console.log("[data] useJob response", out);
            return out;
        },
        enabled: !!token && !!jobId,
        staleTime: STALE_TIME_JOB_MS,
    });
    const { data, isLoading, ...rest } = query;
    return { ...rest, job: data, isLoading };
};

export const usePublish = () => {
    const queryClient = useQueryClient();
    const token = useAuthentication();
    const mutation = useMutation({
        mutationFn: async (jobId: string) => {
            console.log("[data] usePublish request", { jobId, token: token ?? null });
            const out = await new GeometryApiClient(GEOMETRY_API_URL, token).publish(jobId);
            console.log("[data] usePublish response", out);
            return out;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: GALLERIES_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: JOBS_QUERY_KEY });
        },
    });
    return { ...mutation, isLoading: mutation.isPending };
};

export const useUpdateJob = () => {
    const queryClient = useQueryClient();
    const token = useAuthentication();
    const mutation = useMutation({
        mutationFn: async ({
            jobId,
            meta,
            status,
        }: {
            jobId: string;
            meta: Record<string, string>;
            status?: string;
        }) => {
            if (status !== undefined && status !== "success") {
                throw new Error("Only success jobs can be updated");
            }
            const variables = { jobId, meta };
            console.log("[data] useUpdateJob request", { ...variables, token: token ?? null });
            const out = await new GeometryApiClient(GEOMETRY_API_URL, token).updateJob(jobId, meta);
            console.log("[data] useUpdateJob response", out);
            return out;
        },
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: JOB_QUERY_KEY(variables.jobId) });
            queryClient.invalidateQueries({ queryKey: JOBS_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: GALLERIES_QUERY_KEY });
        },
    });
    return { ...mutation, isLoading: mutation.isPending };
};

export const useDeleteJob = () => {
    const queryClient = useQueryClient();
    const token = useAuthentication();
    const mutation = useMutation({
        mutationFn: async (jobId: string) => {
            console.log("[data] useDeleteJob request", { jobId, token: token ?? null });
            await new GeometryApiClient(GEOMETRY_API_URL, token).deleteJob(jobId);
            console.log("[data] useDeleteJob response", "ok");
        },
        onSuccess: (_, jobId) => {
            queryClient.invalidateQueries({ queryKey: JOB_QUERY_KEY(jobId) });
            queryClient.invalidateQueries({ queryKey: JOBS_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: GALLERIES_QUERY_KEY });
        },
    });
    return { ...mutation, isLoading: mutation.isPending };
};

export const useCreateJob = () => {
    const queryClient = useQueryClient();
    const token = useAuthentication();
    const mutation = useMutation({
        mutationFn: async ({
            boundary,
            obstacles,
            title,
        }: {
            boundary: Array<{ x: number; y: number }>;
            obstacles: Array<Array<{ x: number; y: number }>>;
            title?: string;
        }) => {
            const variables = { boundary, obstacles, title };
            console.log("[data] useCreateJob request", { ...variables, token: token ?? null });
            const data = await new GeometryApiClient(GEOMETRY_API_URL, token).createJob(boundary, obstacles, title);
            const out = toDomainJob(fromApiJob(data));
            console.log("[data] useCreateJob response", out);
            return out;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: JOBS_QUERY_KEY });
        },
    });
    return { ...mutation, isLoading: mutation.isPending };
};

export const useValidateJob = () => {
    const token = useAuthentication();
    const mutation = useMutation({
        mutationFn: async (artGallery: ArtGallery) => {
            const { boundary, obstacles } = validateJob(artGallery);
            console.log("[data] useValidateJob request", { artGallery, boundary, obstacles, token: token ?? null });
            const out = await new GeometryApiClient(GEOMETRY_API_URL, token).validatePolygon(boundary, obstacles);
            console.log("[data] useValidateJob response", out);
            return out;
        },
    });
    return { ...mutation, isLoading: mutation.isPending };
};
