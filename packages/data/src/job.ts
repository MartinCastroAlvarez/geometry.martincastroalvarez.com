import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { geometryApiClient } from "./geometry";
import { fromApiJob, toDomainJob } from "./adapters";

export const jobsQueryKey = ["jobs"] as const;
export const jobQueryKey = (jobId: string) => ["jobs", jobId] as const;

export const useJobs = (params?: { nextToken?: string; limit?: number }) => {
    return useQuery({
        queryKey: [...jobsQueryKey, params?.nextToken ?? "", params?.limit ?? 20],
        queryFn: async () => {
            const data = await geometryApiClient.getJobs(params);
            return {
                records: data.records.map((r) => toDomainJob(fromApiJob(r))),
                next_token: data.next_token,
            };
        },
        staleTime: 30 * 1000, // 30 seconds - jobs list updates as processing completes
    });
};

export const useJob = (jobId: string | null) => {
    return useQuery({
        queryKey: jobQueryKey(jobId ?? ""),
        queryFn: async () => {
            if (!jobId) throw new Error("jobId required");
            const data = await geometryApiClient.getJob(jobId);
            return toDomainJob(fromApiJob(data));
        },
        enabled: !!jobId,
        staleTime: 5 * 1000, // 5 seconds - job status changes during processing
    });
};

export const usePublish = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (jobId: string) => geometryApiClient.publish(jobId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["galleries"] });
            queryClient.invalidateQueries({ queryKey: jobsQueryKey });
        },
    });
};

export const useUnpublish = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (jobId: string) => geometryApiClient.unpublish(jobId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["galleries"] });
            queryClient.invalidateQueries({ queryKey: jobsQueryKey });
        },
    });
};

export const useUpdateJob = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ jobId, meta }: { jobId: string; meta: Record<string, string> }) =>
            geometryApiClient.updateJob(jobId, meta),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: jobQueryKey(variables.jobId) });
            queryClient.invalidateQueries({ queryKey: jobsQueryKey });
            queryClient.invalidateQueries({ queryKey: ["galleries"] });
        },
    });
};
