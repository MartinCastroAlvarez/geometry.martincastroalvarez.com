/**
 * Skeleton for Home (galleries list). Grid 2×4 of EditorSkeleton.
 * WithHomePageSkeleton shows skeleton when loading, otherwise renders children.
 */
import type { ReactNode } from "react";
import { Skeleton, Container } from "@geometry/ui";
import { EditorSkeleton } from "@geometry/editor";

const ROWS = 4;
const COLS = 2;
const CELLS = ROWS * COLS;
/** Height of each editor skeleton (px). Width is 100%. */
const EDITOR_SKELETON_HEIGHT = 220;

export const HomePageSkeleton = () => (
    <Skeleton>
        <Container padded spaced>
            <Container name="geometry-home-skeleton-grid">
                {Array.from({ length: CELLS }, (_, i) => (
                    <Container key={i} size={12 / COLS}>
                        <EditorSkeleton size={EDITOR_SKELETON_HEIGHT} />
                    </Container>
                ))}
            </Container>
        </Container>
    </Skeleton>
);

export const WithHomePageSkeleton = ({ loading, children }: { loading: boolean; children: ReactNode }) =>
    loading ? <HomePageSkeleton /> : <>{children}</>;
