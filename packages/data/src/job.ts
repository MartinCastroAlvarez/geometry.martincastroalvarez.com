/**
 * React Query hooks for jobs (list, single, publish, unpublish, update).
 *
 * Context: Jobs represent art-gallery processing pipelines. Hooks call Geometry API
 * /v1/jobs, normalize with fromApiJob + toDomainJob. Query keys and stale times from constants.ts
 * (JOBS_QUERY_KEY, JOB_QUERY_KEY, STALE_TIME_*). Mutations invalidate jobs and
 * galleries caches so the UI stays in sync after publish/unpublish/update.
 *
 * Example:
 *   const { data } = useJobs({ limit: 20 });
 *   const { data: job } = useJob(jobId);
 *   const publish = usePublish();  publish.mutate(jobId);
 *   const update = useUpdateJob(); update.mutate({ jobId, meta: { title: "New" } });
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { geometryApiClient } from "./geometry";
import { fromApiJob, toDomainJob } from "./adapters";
import {
    GALLERIES_QUERY_KEY,
    JOBS_QUERY_KEY,
    JOB_QUERY_KEY,
    STALE_TIME_JOBS_LIST_MS,
    STALE_TIME_JOB_MS,
} from "./constants";

export { JOBS_QUERY_KEY, JOB_QUERY_KEY } from "./constants";

export const useJobs = (params?: { nextToken?: string; limit?: number }) => {
    return useQuery({
        queryKey: [...JOBS_QUERY_KEY, params?.nextToken ?? "", params?.limit ?? 20],
        queryFn: async () => {
            const data = await geometryApiClient.getJobs(params);
            return {
                records: data.records.map((r) => toDomainJob(fromApiJob(r))),
                next_token: data.next_token,
            };
        },
        staleTime: STALE_TIME_JOBS_LIST_MS,
    });
};

export const useJob = (jobId: string | null) => {
    return useQuery({
        queryKey: JOB_QUERY_KEY(jobId ?? ""),
        queryFn: async () => {
            if (!jobId) throw new Error("jobId required");
            const data = await geometryApiClient.getJob(jobId);
            return toDomainJob(fromApiJob(data));
        },
        enabled: !!jobId,
        staleTime: STALE_TIME_JOB_MS,
    });
};

export const usePublish = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (jobId: string) => geometryApiClient.publish(jobId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: GALLERIES_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: JOBS_QUERY_KEY });
        },
    });
};

export const useUnpublish = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (jobId: string) => geometryApiClient.unpublish(jobId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: GALLERIES_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: JOBS_QUERY_KEY });
        },
    });
};

export const useUpdateJob = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ jobId, meta }: { jobId: string; meta: Record<string, string> }) =>
            geometryApiClient.updateJob(jobId, meta),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: JOB_QUERY_KEY(variables.jobId) });
            queryClient.invalidateQueries({ queryKey: JOBS_QUERY_KEY });
            queryClient.invalidateQueries({ queryKey: GALLERIES_QUERY_KEY });
        },
    });
};
