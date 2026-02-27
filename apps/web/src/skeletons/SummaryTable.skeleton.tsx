/**
 * Skeleton for the validation summary table (EditorPage).
 * Matches the layout: container with rows of badge + note (left badge, right text).
 */
import { Container, BadgeSkeleton, TextSkeleton } from "@geometry/ui";

const ROW_COUNT = 7;

export const SummaryTableSkeleton = () => (
    <Container padded spaced rounded solid size={12}>
        {Array.from({ length: ROW_COUNT }, (_, i) => (
            <Container key={i} size={12} spaced left middle>
                <Container size={3} left middle>
                    <BadgeSkeleton width="4rem" />
                </Container>
                <Container size={9} left middle>
                    <TextSkeleton sm width={i % 2 === 0 ? "80%" : "60%"} />
                </Container>
            </Container>
        ))}
    </Container>
);
