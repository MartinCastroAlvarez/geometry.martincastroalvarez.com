/**
 * Skeleton for EditorSummaryTable: requirements list or validation results.
 * Used when validation is loading (results variant) or as placeholder for the summary column.
 */
import { Skeleton, Container, BadgeSkeleton, BulletSkeleton, TextSkeleton } from "@geometry/ui";

const SUMMARY_ROW_COUNT = 7;
const SUMMARY_RESULT_ROW_WIDTHS: (string | number)[] = ["75%", "82%", "68%", "90%", "72%", "85%", "78%"];
const SUMMARY_REQUIREMENT_ROW_WIDTHS: (string | number)[] = ["88%", "72%", "85%", "90%", "78%", "82%", "75%"];

export type SummaryTableSkeletonVariant = "requirements" | "results";

export interface SummaryTableSkeletonProps {
    variant?: SummaryTableSkeletonVariant;
}

export const SummaryTableSkeleton = ({ variant = "results" }: SummaryTableSkeletonProps) => (
    <Skeleton>
        <Container padded spaced rounded left>
            {variant === "requirements"
                ? Array.from({ length: SUMMARY_ROW_COUNT }, (_, i) => (
                    <Container key={i}>
                        <BulletSkeleton sm width={SUMMARY_REQUIREMENT_ROW_WIDTHS[i]} />
                    </Container>
                ))
                : Array.from({ length: SUMMARY_ROW_COUNT }, (_, i) => (
                    <Container key={i}>
                        <div className="flex items-start gap-2 min-h-[1.5rem]">
                            <span className="shrink-0 mt-0.5">
                                <BadgeSkeleton width="4rem" />
                            </span>
                            <span className="flex-1 min-w-0">
                                <TextSkeleton sm width={SUMMARY_RESULT_ROW_WIDTHS[i]} lines={1} />
                            </span>
                        </div>
                    </Container>
                ))}
        </Container>
    </Skeleton>
);
