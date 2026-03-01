/**
 * Skeleton for Jobs list page. Grid 2×4 of EditorSkeleton (same as HomePage).
 */
import { Skeleton, Container } from "@geometry/ui";
import { EditorSkeleton } from "@geometry/editor";

const ROWS = 4;
const COLS = 2;
const CELLS = ROWS * COLS;
/** Height of each editor skeleton (px). Width is 100%. */
const EDITOR_SKELETON_HEIGHT = 220;

export const JobsPageSkeleton = () => (
    <Skeleton>
        <Container padded spaced>
            <Container name="geometry-jobs-skeleton-grid">
                {Array.from({ length: CELLS }, (_, i) => (
                    <Container key={i} size={12 / COLS}>
                        <EditorSkeleton size={EDITOR_SKELETON_HEIGHT} />
                    </Container>
                ))}
            </Container>
        </Container>
    </Skeleton>
);
