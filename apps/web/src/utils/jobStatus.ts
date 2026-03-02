/**
 * Display status for a job: if the job is still PENDING (processing) but was created
 * more than 1 hour ago, treat it as FAILED for display purposes.
 */
import type { Job } from "@geometry/domain";
import { Status } from "@geometry/domain";

const ONE_HOUR_MS = 60 * 60 * 1000;

export function getDisplayStatus(job: Job): Status {
    if (job.status !== Status.PENDING) return job.status;
    const created = job.created_at ? new Date(job.created_at).getTime() : 0;
    if (!created || Number.isNaN(created)) return job.status;
    const oneHourAgo = Date.now() - ONE_HOUR_MS;
    return created < oneHourAgo ? Status.FAILED : job.status;
}
