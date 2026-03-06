/**
 * Display status for a job. FAILED and SUCCESS always display as-is (status takes precedence).
 * Only for PENDING: if updated_at is 1 hour ago or more, show FAILED (stale); otherwise show PENDING.
 */
import type { Job } from "@geometry/domain";
import { Status } from "@geometry/domain";

const ONE_HOUR_MS = 60 * 60 * 1000;

function getUpdatedAtMs(job: Job): number | null {
    if (!job.updated_at) return null;
    const ms = new Date(job.updated_at).getTime();
    return Number.isNaN(ms) ? null : ms;
}

export function getDisplayStatus(job: Job): Status {
    if (job.status === Status.FAILED || job.status === Status.SUCCESS) return job.status;
    if (job.status !== Status.PENDING) return job.status;
    const updated = getUpdatedAtMs(job);
    if (updated == null) return job.status;
    const oneHourAgo = Date.now() - ONE_HOUR_MS;
    return updated < oneHourAgo ? Status.FAILED : job.status;
}
