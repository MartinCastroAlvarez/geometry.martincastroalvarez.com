/**
 * Editor info table: validation requirement keys when no summary is shown.
 *
 * Context: Renders a bullet list of validation rules (boundary convex/ccw/simple, obstacle convex/cw/
 * contained/no-overlap) with a check icon. Used by EditorSummaryTable when summary is not passed
 * or has no rows, so the user sees requirements before or instead of results. Uses @geometry/ui
 * Bullet and Container; labels come from @geometry/i18n (validation.requirement*).
 *
 * Example:
 *   <EditorInfoTable />
 */
import { CircleCheck } from "lucide-react";
import { useLocale } from "@geometry/i18n";
import { Container, Bullet } from "@geometry/ui";

const REQUIREMENT_KEYS = [
    "validation.requirementBoundaryConvex",
    "validation.requirementBoundaryCcw",
    "validation.requirementBoundarySimple",
    "validation.requirementObstacleConvex",
    "validation.requirementObstacleCw",
    "validation.requirementObstacleContained",
    "validation.requirementObstacleNoOverlap",
] as const;

export const EditorInfoTable = () => {
    const { t } = useLocale();
    return (
        <Container padded spaced rounded solid left>
            {REQUIREMENT_KEYS.map((key) => (
                <Container key={key}>
                    <Bullet sm left icon={<CircleCheck className="size-4 text-slate-400 shrink-0" aria-hidden />}>
                        {t(key)}
                    </Bullet>
                </Container>
            ))}
        </Container>
    );
};
