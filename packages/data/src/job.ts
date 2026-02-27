/**
 * React Query hooks for jobs (list, single, publish, unpublish, update, create).
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
import { fromApiJob, toDomainJob } from "./adapters";
import {
    GEOMETRY_API_URL,
    GALLERIES_QUERY_KEY,
    JOBS_QUERY_KEY,
    JOB_QUERY_KEY,
    STALE_TIME_JOBS_LIST_MS,
    STALE_TIME_JOB_MS,
} from "./constants";
import { useAuthentication } from "./useAuthToken";

export { JOBS_QUERY_KEY, JOB_QUERY_KEY } from "./constants";

export const useJobs = (params?: { nextToken?: string; limit?: number }) => {
    const token = useAuthentication();
    const query = useQuery({
        queryKey: [...JOBS_QUERY_KEY, params?.nextToken ?? "", params?.limit ?? 20, token ?? ""],
        queryFn: async () => {
            const data = await new GeometryApiClient(GEOMETRY_API_URL, token).getJobs(params);
            return {
                records: data.records.map((r) => toDomainJob(fromApiJob(r))),
                next_token: data.next_token,
            };
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
            const data = await new GeometryApiClient(GEOMETRY_API_URL, token).getJob(jobId);
            return toDomainJob(fromApiJob(data));
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
        mutationFn: (jobId: string) => new GeometryApiClient(GEOMETRY_API_URL, token).publish(jobId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: GALLERIES_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: JOBS_QUERY_KEY });
        },
    });
    return { ...mutation, isLoading: mutation.isPending };
};

export const useUnpublish = () => {
    const queryClient = useQueryClient();
    const token = useAuthentication();
    const mutation = useMutation({
        mutationFn: (jobId: string) => new GeometryApiClient(GEOMETRY_API_URL, token).unpublish(jobId),
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
        mutationFn: ({ jobId, meta }: { jobId: string; meta: Record<string, string> }) =>
            new GeometryApiClient(GEOMETRY_API_URL, token).updateJob(jobId, meta),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: JOB_QUERY_KEY(variables.jobId) });
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
        mutationFn: ({
            boundary,
            obstacles,
        }: {
            boundary: Array<{ x: number; y: number }>;
            obstacles: Array<Array<{ x: number; y: number }>>;
        }) => new GeometryApiClient(GEOMETRY_API_URL, token).createJob(boundary, obstacles),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: JOBS_QUERY_KEY });
        },
    });
    return { ...mutation, isLoading: mutation.isPending };
};
