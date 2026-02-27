export interface Job {
    id: string;
    status: string;
    stage: string;
    meta: Record<string, unknown>;
    stdout: Record<string, unknown>;
}
