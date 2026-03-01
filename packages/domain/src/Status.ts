/**
 * Task status: PENDING, SUCCESS, or FAILED.
 *
 * Context: Matches api/enums.py Status. Used for job status and validation summary
 * overall status. Parse API string with Status.parse().
 *
 * Example:
 *   Status.parse("success") === Status.SUCCESS
 *   job.status === Status.SUCCESS
 */
export enum Status {
    PENDING = "pending",
    SUCCESS = "success",
    FAILED = "failed",
}

/**
 * Coerce string to Status; throws if invalid (matches API validation).
 */
export function parseStatus(value: string | null | undefined): Status {
    if (value == null || (typeof value === "string" && !value.trim())) {
        throw new Error("status is required and must be a non-empty string");
    }
    const raw = (typeof value === "string" ? value : String(value)).trim().toLowerCase();
    const found = Object.values(Status).find((s) => s === raw);
    if (found != null) return found;
    throw new Error(
        `status must be one of [${Status.PENDING}, ${Status.FAILED}, ${Status.SUCCESS}], got ${JSON.stringify(raw)}`
    );
}
