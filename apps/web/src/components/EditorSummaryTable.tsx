/**
 * Editor summary table: validation results or requirement list (via EditorInfoTable).
 *
 * Context: When a Summary is provided with rows, renders each check as a Badge (ERROR/SUCCESS/other)
 * plus optional localized note, sorted so errors appear first. When summary is null/undefined or
 * has no rows, delegates to EditorInfoTable to show the requirement list. Uses @geometry/domain
 * Summary type and @geometry/i18n for note translation (validation.*).
 *
 * The API may return either validation codes (e.g. POLYGON_NOT_CCW) or English messages; we map
 * known English messages to codes so the UI always shows the localized string from the current locale.
 *
 * Example:
 *   <EditorSummaryTable summary={validationResult ?? undefined} />
 *   // With no summary: <EditorSummaryTable />  → shows EditorInfoTable
 */
import { useLocale } from "@geometry/i18n";
import { Container, Bullet } from "@geometry/ui";
import type { Summary } from "@geometry/domain";
import { EditorInfoTable } from "./EditorInfoTable";

/** Map API English messages to validation codes so we can always resolve validation.* in the current locale. */
const VALIDATION_NOTE_EN_TO_CODE: Record<string, string> = {
    "Polygon is convex.": "POLYGON_CONVEX_OK",
    "Polygon is not convex.": "POLYGON_NOT_CONVEX",
    "Polygon is counter-clockwise.": "POLYGON_CCW_OK",
    "Polygon is not counter-clockwise.": "POLYGON_NOT_CCW",
    "Polygon is simple (no self-intersection).": "POLYGON_SIMPLE_OK",
    "Polygon is not simple (self-intersects).": "POLYGON_NOT_SIMPLE",
    "Obstacle is convex.": "OBSTACLE_CONVEX_OK",
    "Obstacle is not convex.": "OBSTACLE_NOT_CONVEX",
    "Obstacle is clockwise.": "OBSTACLE_CW_OK",
    "Obstacle is not clockwise.": "OBSTACLE_NOT_CW",
    "Obstacle is fully inside the boundary.": "OBSTACLE_CONTAINED_OK",
    "Obstacle is not fully inside the boundary.": "OBSTACLE_NOT_CONTAINED",
    "Obstacle overlaps another obstacle.": "OBSTACLE_OVERLAPS",
    "Obstacle does not overlap others.": "OBSTACLE_NO_OVERLAP",
    "Check skipped (invalid or earlier error).": "CHECK_SKIPPED",
    "All validations passed.": "ALL_VALIDATIONS_PASSED",
    "One or more validations failed or are pending.": "VALIDATIONS_FAILED_OR_PENDING",
};

const summaryRows = (summary: Summary): { key: string; status: string; note: string }[] => {
    const statusKeys = Object.keys(summary).filter((k) => !k.endsWith(".note"));
    return statusKeys
        .sort()
        .map((key) => {
            const status = summary[key] ?? "pending";
            const note = summary[`${key}.note`] ?? "";
            return { key, status: status === "failed" ? "ERROR" : status.toUpperCase(), note };
        });
};

type EditorSummaryTableProps = { summary?: Summary | null };

export const EditorSummaryTable = ({ summary }: EditorSummaryTableProps) => {
    const { t } = useLocale();
    const rows = summary ? summaryRows(summary) : [];
    if (rows.length === 0) {
        return (
            <EditorInfoTable
                excludeRequirements={[
                    "validation.requirementBoundaryCcw",
                    "validation.requirementObstacleCw",
                ]}
            />
        );
    }
    const order = (a: string, b: string) => (a === "ERROR" ? -1 : a === "SUCCESS" ? 0 : 1) - (b === "ERROR" ? -1 : b === "SUCCESS" ? 0 : 1);
    const sorted = [...rows].sort((a, b) => order(a.status, b.status));
    const getLocalizedNote = (note: string): string => {
        if (!note) return "";
        const translationKey = `validation.${note}`;
        const translated = t(translationKey);
        if (translated !== translationKey) return translated;
        const code = VALIDATION_NOTE_EN_TO_CODE[note];
        if (code) return t(`validation.${code}`);
        return note;
    };

    return (
        <Container padded spaced rounded left>
            {sorted.map(({ key, status, note }) => (
                <Container key={key}>
                    <Bullet
                        danger={status === "ERROR"}
                        success={status === "SUCCESS"}
                        sm
                        left
                    >
                        {getLocalizedNote(note)}
                    </Bullet>
                </Container>
            ))}
        </Container>
    );
};
