/**
 * Skeleton for EditorReview: mirrors real layout — form row (Validate/Submit) then
 * requirement/result list. Same Container hierarchy as EditorReview (form + table).
 */
import { Skeleton, Container, BulletSkeleton, ButtonSkeleton } from "@geometry/ui";

const ROW_COUNT = 7;
/** Approximate relative lengths for requirement bullets (Boundary/Obstacle text). */
const ROW_WIDTHS: (string | number)[] = ["85%", "90%", "88%", "82%", "90%", "88%", "78%"];

export type EditorReviewSkeletonVariant = "requirements" | "results";

export interface EditorReviewSkeletonProps {
    variant?: EditorReviewSkeletonVariant;
}

export const EditorReviewSkeleton = ({ variant: _variant = "results" }: EditorReviewSkeletonProps) => (
    <Skeleton className="w-full">
        {/* Form: same as EditorReview — Container (padded spaced left) > form container > buttons */}
        <Container padded spaced left>
            <Container name="geometry-editor-form" middle left spaced>
                <div className="flex flex-row flex-wrap items-center gap-2 w-full justify-start">
                    <ButtonSkeleton sm width="5rem" />
                    <ButtonSkeleton sm width="5rem" />
                </div>
            </Container>
        </Container>
        {/* Table: same as EditorInfoTable / EditorSummaryTable — single rounded container, one row per bullet */}
        <Container padded spaced left>
            <Container padded spaced rounded left>
                {Array.from({ length: ROW_COUNT }, (_, i) => (
                    <Container key={i}>
                        <BulletSkeleton sm width={ROW_WIDTHS[i]} />
                    </Container>
                ))}
            </Container>
        </Container>
    </Skeleton>
);
