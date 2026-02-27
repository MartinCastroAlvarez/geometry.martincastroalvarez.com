/**
 * Skeleton for Home (galleries list). Grid 2×4 of EditorSkeleton.
 */
import { Container } from "@geometry/ui";
import { EditorSkeleton } from "@geometry/editor";

const ROWS = 4;
const COLS = 2;
const CELLS = ROWS * COLS;
/** Height of each editor skeleton (px). Width is 100%. */
const EDITOR_SKELETON_HEIGHT = 220;

export const HomePageSkeleton = () => (
    <Container padded spaced size={12}>
        <Container size={12} name="geometry-home-skeleton-grid">
            {Array.from({ length: CELLS }, (_, i) => (
                <Container key={i} size={12 / COLS}>
                    <EditorSkeleton size={EDITOR_SKELETON_HEIGHT} />
                </Container>
            ))}
        </Container>
    </Container>
);
