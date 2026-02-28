/**
 * Skeleton for EditorReview: matches real layout — form row (Validate/Submit) on top,
 * then a Container with bullet rows (validation list or requirements).
 */
import { Skeleton, Container, BulletSkeleton, ButtonSkeleton } from "@geometry/ui";

const ROW_COUNT = 7;
const ROW_WIDTHS: (string | number)[] = ["92%", "88%", "95%", "85%", "90%", "87%", "93%"];

export type EditorReviewSkeletonVariant = "requirements" | "results";

export interface EditorReviewSkeletonProps {
    variant?: EditorReviewSkeletonVariant;
}

export const EditorReviewSkeleton = ({ variant: _variant = "results" }: EditorReviewSkeletonProps) => (
    <Skeleton className="min-h-[280px] w-full">
        {/* Form row: same structure as EditorReview → EditorForm (Validate/Submit buttons) */}
        <Container padded spaced left>
            <Container name="geometry-editor-form" middle left spaced>
                <div className="flex flex-row flex-wrap items-center gap-2 w-full justify-start">
                    <ButtonSkeleton sm width="5rem" />
                    <ButtonSkeleton sm width="5rem" />
                </div>
            </Container>
        </Container>
        {/* Table: bullet rows like EditorSummaryTable / EditorInfoTable */}
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
