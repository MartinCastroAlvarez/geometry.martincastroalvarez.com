/**
 * Editor review: form (Validate/Submit) above one of two tables.
 * When summary is passed (and has rows), shows validation results; otherwise shows the info table.
 * When artGallery is passed, shows the form in a Container above the table.
 */
import { useLocale } from "@geometry/i18n";
import { Container, Scrollable, Bullet, Toolbar, Button, Problem, Inspector } from "@geometry/ui";
import type { ArtGallery, Summary } from "@geometry/domain";
import { EditorReviewSkeleton } from "./EditorReview.skeleton";

/** Shared height for the three review tables (info, summary); content scrolls when larger. */
const REVIEW_TABLE_CONTAINER_HEIGHT_PX = 500;

/** Max height of the Inspector (JSON view) in pixels. */
const INSPECTOR_SIZE_PX = 500;

const REQUIREMENT_KEYS = [
    "validation.requirementBoundaryCcw",
    "validation.requirementBoundarySimple",
    "validation.requirementObstacleSimple",
    "validation.requirementObstacleCw",
    "validation.requirementObstacleContained",
    "validation.requirementObstacleNoOverlap",
] as const;

type EditorInfoTableProps = { excludeRequirements?: string[] };

const EditorInfoTable = ({ excludeRequirements }: EditorInfoTableProps = {}) => {
    const { t } = useLocale();
    const keys = excludeRequirements?.length
        ? REQUIREMENT_KEYS.filter((k) => !excludeRequirements.includes(k))
        : [...REQUIREMENT_KEYS];
    return (
        <Scrollable padded spaced rounded left height={REVIEW_TABLE_CONTAINER_HEIGHT_PX}>
            {keys.map((key) => (
                <Container key={key}>
                    <Bullet sm left>
                        {t(key)}
                    </Bullet>
                </Container>
            ))}
        </Scrollable>
    );
};

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
    "Obstacle is simple (no self-intersection).": "OBSTACLE_SIMPLE_OK",
    "Obstacle is not simple (self-intersects).": "OBSTACLE_NOT_SIMPLE",
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
            const val = summary[key];
            const statusStr = val == null ? "pending" : (typeof val === "string" ? val : val);
            const note = summary[`${key}.note`] ?? "";
            return { key, status: statusStr === "failed" ? "ERROR" : statusStr.toUpperCase(), note };
        });
};

type EditorSummaryTableProps = { summary?: Summary | null };

const EditorSummaryTable = ({ summary }: EditorSummaryTableProps) => {
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
    // Deduplicate by (status, note) so the same failure reason is shown once (e.g. 2 obstacles failing for same reason).
    const seen = new Set<string>();
    const deduped = sorted.filter((row) => {
        const id = `${row.status}:${row.note}`;
        if (seen.has(id)) return false;
        seen.add(id);
        return true;
    });
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
        <Scrollable padded spaced rounded left height={REVIEW_TABLE_CONTAINER_HEIGHT_PX}>
            {deduped.map(({ status, note }) => (
                <Container key={`${status}:${note}`}>
                    <Bullet
                        danger={status === "ERROR"}
                        success={status === "SUCCESS"}
                        sm
                        left
                        truncate
                        spaced
                    >
                        {getLocalizedNote(note)}
                    </Bullet>
                </Container>
            ))}
        </Scrollable>
    );
};

type EditorInspectorTableProps = { artGallery: ArtGallery | null };

const EditorInspectorTable = ({ artGallery }: EditorInspectorTableProps) => {
    if (artGallery == null) return null;
    return (
        <Scrollable name="geometry-inspector-scroll" height={INSPECTOR_SIZE_PX}>
            <Inspector data={artGallery.toDict()} size={INSPECTOR_SIZE_PX} />
        </Scrollable>
    );
};

type EditorFormProps = {
    artGallery: ArtGallery | null;
    onValidate?: () => void;
    onSubmit?: () => void;
    disabled?: boolean;
};

const EditorForm = ({ artGallery, onValidate, onSubmit, disabled = false }: EditorFormProps) => {
    const { t } = useLocale();
    if (artGallery == null || artGallery.boundary.points.length < 1) return null;
    return (
        <Container name="geometry-editor-form" middle left spaced>
            <Toolbar left>
                {onValidate != null && (
                    <Button sm onClick={onValidate} disabled={disabled}>
                        {t("editor.validate")}
                    </Button>
                )}
                {onSubmit != null && (
                    <Button sm primary onClick={onSubmit} disabled={disabled}>
                        {t("editor.submit")}
                    </Button>
                )}
            </Toolbar>
        </Container>
    );
};

export interface EditorReviewProps {
    summary?: Summary | null;
    /** When passed, EditorForm (Validate/Submit) is shown in a Container above the table. */
    artGallery?: ArtGallery | null;
    /** Optional error message shown below the form buttons, above the table. */
    errorMessage?: string | null;
    isLoading?: boolean;
    onValidate?: () => void;
    onSubmit?: () => void;
    disabled?: boolean;
}

export const EditorReview = ({
    summary,
    artGallery,
    errorMessage = null,
    isLoading = false,
    onValidate,
    onSubmit,
    disabled = false,
}: EditorReviewProps) => {
    if (isLoading) {
        return <EditorReviewSkeleton variant="results" />;
    }
    const hasSummaryRows = summary != null && summaryRows(summary).length > 0;
    return (
        <>
            {artGallery != null && artGallery.boundary.points.length >= 1 && (
                <Container padded spaced left>
                    <EditorForm
                        artGallery={artGallery}
                        onValidate={onValidate}
                        onSubmit={onSubmit}
                        disabled={disabled}
                    />
                </Container>
            )}
            {errorMessage != null && errorMessage.trim() !== "" && (
                <Container padded spaced left>
                    <Problem align="left">{errorMessage}</Problem>
                </Container>
            )}
            <Container padded spaced left>
                {hasSummaryRows ? (
                    <EditorSummaryTable summary={summary!} />
                ) : artGallery != null ? (
                    <EditorInspectorTable artGallery={artGallery} />
                ) : summary != null ? (
                    <EditorInfoTable
                        excludeRequirements={[
                            "validation.requirementBoundaryCcw",
                            "validation.requirementObstacleCw",
                        ]}
                    />
                ) : (
                    <EditorInfoTable />
                )}
            </Container>
        </>
    );
};
