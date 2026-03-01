/**
 * Job: async job record (id, status, step_name, meta, stdout).
 *
 * Context: Reflects backend job entity; status is Status (PENDING/SUCCESS/FAILED); step_name, meta, stdout unchanged.
 * Used by job polling and job pages. When the job input (stdin) contains valid boundary and obstacles,
 * artGallery may be populated by adapters so the UI can display the gallery (e.g. in Viewer).
 *
 * Example:
 *   const job: Job = { id: 'j1', status: Status.SUCCESS, step_name: 'solve', meta: {}, stdout: {}, artGallery };
 */
import type { Status } from "./Status";
import type { ArtGallery } from "./ArtGallery";

export interface Job {
    id: string;
    status: Status;
    step_name: string;
    meta: Record<string, unknown>;
    stdin?: Record<string, unknown>;
    stdout: Record<string, unknown>;
    stderr?: Record<string, unknown>;
    /** ISO date strings from API (created_at, updated_at). */
    created_at?: string;
    updated_at?: string;
    /** When present, the job input had valid boundary and obstacles; see data adapters. */
    artGallery?: ArtGallery;
    /** Child job IDs from the API (parent has children_ids). */
    children_ids?: string[];
}
