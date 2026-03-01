/**
 * Summary: validation output from polygon validation API.
 *
 * Context: Flat record of check keys (e.g. "polygon.convex", "obstacles.0.contained")
 * with string values for sub-checks; the overall "status" key is Status (PENDING/SUCCESS/FAILED).
 * The API returns string values; use parseSummaryFromApi() to build Summary from the response.
 * Used by EditorPage and EditorReview to display validation results and to gate the Submit button.
 *
 * Example:
 *   const summary: Summary = parseSummaryFromApi(await response.json());
 *   isValidationSuccess(summary) // true when summary.status === Status.SUCCESS
 */
import { parseStatus, Status } from "./Status";

export const SUMMARY_STATUS_KEY = "status" as const;

/** Overall validation status is Status; other keys are string (e.g. "status.note", "polygon.convex"). */
export interface Summary {
    [SUMMARY_STATUS_KEY]: Status;
    [key: string]: string | Status | undefined;
}

/**
 * Build Summary from API response (parses "status" string into Status).
 */
export function parseSummaryFromApi(raw: Record<string, string>): Summary {
    return { ...raw, [SUMMARY_STATUS_KEY]: parseStatus(raw[SUMMARY_STATUS_KEY]) };
}

/**
 * Returns true only when the validation response has overall status SUCCESS (all sub-validations passed).
 */
export const isValidationSuccess = (summary: Summary): boolean =>
    summary.status === Status.SUCCESS;
