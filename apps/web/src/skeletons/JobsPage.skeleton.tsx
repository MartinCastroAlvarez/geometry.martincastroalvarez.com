/**
 * Skeleton for Jobs list page. Grid 2×4 of EditorSkeleton (same as HomePage).
 * WithJobsPageSkeleton shows skeleton when loading, otherwise renders children.
 */
import type { ReactNode } from "react";
import { Skeleton } from "@geometry/ui";
import { EditorSkeleton } from "@geometry/editor";

const ROWS = 4;
const COLS = 2;
const CELLS = ROWS * COLS;
/** Height of each editor skeleton (px). Width is 100%. */
const EDITOR_SKELETON_HEIGHT = 220;

export const JobsPageSkeleton = () => (
    <Skeleton padded spaced>
        <Skeleton name="geometry-jobs-skeleton-grid">
            {Array.from({ length: CELLS }, (_, i) => (
                <Skeleton key={i} size={12 / COLS}>
                    <EditorSkeleton size={EDITOR_SKELETON_HEIGHT} />
                </Skeleton>
            ))}
        </Skeleton>
    </Skeleton>
);

export function WithJobsPageSkeleton({ loading, children }: { loading: boolean; children: ReactNode }) {
    return loading ? <JobsPageSkeleton /> : <>{children}</>;
}
