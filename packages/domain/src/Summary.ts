/**
 * Summary: validation output from polygon validation API.
 *
 * Context: Flat record of check keys (e.g. "polygon.convex", "obstacles.0.contained")
 * with string values (status for check keys, message for "*.note" keys).
 * The API always returns "status" (overall: "success" | "failed" | "pending") and
 * "status.note". Used by EditorPage and SummaryTable to display validation results
 * and to gate the Submit button (only when status === "success").
 *
 * Example:
 *   const summary: Summary = { "status": "success", "status.note": "All validations passed.", "polygon.convex": "success" };
 */

export type Summary = Record<string, string>;

/** Key for overall validation status; value is "success" | "failed" | "pending". */
export const SUMMARY_STATUS_KEY = "status" as const;

/**
 * Returns true only when the validation response has overall status "success"
 * (all sub-validations passed). Use to show the Submit button.
 */
export function isValidationSuccess(summary: Summary): boolean {
    return summary[SUMMARY_STATUS_KEY] === "success";
}
