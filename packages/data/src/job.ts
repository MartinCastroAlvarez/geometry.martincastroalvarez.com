import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { geometryApiClient } from "./geometry";
import { JobModel } from "./models";

export const jobsQueryKey = ["jobs"] as const;
export const jobQueryKey = (jobId: string) => ["jobs", jobId] as const;

export function useJobs(params?: { nextToken?: string; limit?: number }) {
    return useQuery({
        queryKey: [...jobsQueryKey, params?.nextToken ?? "", params?.limit ?? 20],
        queryFn: async () => {
            const data = await geometryApiClient.getJobs(params);
            return {
                records: data.records.map((r) => JobModel.fromApi(r)),
                next_token: data.next_token,
            };
        },
        staleTime: 30 * 1000, // 30 seconds - jobs list updates as processing completes
    });
}

export function useJob(jobId: string | null) {
    return useQuery({
        queryKey: jobQueryKey(jobId ?? ""),
        queryFn: async () => {
            if (!jobId) throw new Error("jobId required");
            const data = await geometryApiClient.getJob(jobId);
            return JobModel.fromApi(data);
        },
        enabled: !!jobId,
        staleTime: 5 * 1000, // 5 seconds - job status changes during processing
    });
}

export function usePublish() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (jobId: string) => geometryApiClient.publish(jobId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["galleries"] });
            queryClient.invalidateQueries({ queryKey: jobsQueryKey });
        },
    });
}

export function useUnpublish() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (jobId: string) => geometryApiClient.unpublish(jobId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["galleries"] });
            queryClient.invalidateQueries({ queryKey: jobsQueryKey });
        },
    });
}

export function useUpdateJob() {
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
}
