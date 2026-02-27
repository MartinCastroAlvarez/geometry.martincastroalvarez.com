/**
 * Job: async job record (id, status, stage, meta, stdout).
 *
 * Context: Reflects backend job entity; status/stage are strings; meta and stdout are flexible records.
 * Used by job polling and job pages.
 *
 * Example:
 *   const job: Job = { id: 'j1', status: 'running', stage: 'solve', meta: {}, stdout: {} };
 */
export interface Job {
    id: string;
    status: string;
    stage: string;
    meta: Record<string, unknown>;
    stdout: Record<string, unknown>;
}
