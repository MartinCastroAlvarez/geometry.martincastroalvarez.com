/**
 * Job: async job record (id, status, stage, meta, stdout).
 *
 * Context: Reflects backend job entity; status is Status (PENDING/SUCCESS/FAILED); stage, meta, stdout unchanged.
 * Used by job polling and job pages. When the job input (stdin) contains valid boundary and obstacles,
 * artGallery may be populated by adapters so the UI can display the gallery (e.g. in Viewer).
 *
 * Example:
 *   const job: Job = { id: 'j1', status: Status.SUCCESS, stage: 'solve', meta: {}, stdout: {}, artGallery };
 */
import type { Status } from "./Status";
import type { ArtGallery } from "./ArtGallery";

export interface Job {
    id: string;
    status: Status;
    stage: string;
    meta: Record<string, unknown>;
    stdout: Record<string, unknown>;
    /** When present, the job input had valid boundary and obstacles; see data adapters. */
    artGallery?: ArtGallery;
}
