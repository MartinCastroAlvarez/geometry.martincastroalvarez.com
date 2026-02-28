/**
 * Skeleton for Editor page: title input, two-column layout (editor | summary), tip at bottom.
 * Matches EditorPage layout: centered title, editor (8 cols) | summary (4 cols) on desktop,
 * stacked on mobile; EditorSkeleton matches Editor (grid, pulse, polygon).
 */
import type { ReactNode } from "react";
import { Container, InputSkeleton, TextSkeleton, useDevice } from "@geometry/ui";
import { EditorSkeleton } from "@geometry/editor";
import { SummaryTableSkeleton } from "./EditorSummaryTable.skeleton";

const EDITOR_SKELETON_HEIGHT = 550;
const EDITOR_COL_DESKTOP = 8;
const SUMMARY_COL_DESKTOP = 4;

export const EditorPageSkeleton = () => {
    const { isMobile } = useDevice();

    return (
        <Container padded spaced>
            <Container padded spaced middle center>
                <div className="max-w-md w-full">
                    <InputSkeleton width="100%" />
                </div>
            </Container>
            <Container>
                <Container padded name="geometry-editor-wrapper w-full max-h-[70vh]" size={isMobile ? 12 : EDITOR_COL_DESKTOP}>
                    <EditorSkeleton size={EDITOR_SKELETON_HEIGHT} />
                </Container>
                <Container padded spaced left size={isMobile ? 12 : SUMMARY_COL_DESKTOP}>
                    <SummaryTableSkeleton variant="requirements" />
                </Container>
            </Container>
            <Container padded spaced center>
                <TextSkeleton sm width="80%" />
            </Container>
        </Container>
    );
};

export function WithEditorPageSkeleton({ loading, children }: { loading: boolean; children: ReactNode }) {
    return loading ? <EditorPageSkeleton /> : <>{children}</>;
}
