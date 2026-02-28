/**
 * Skeleton for Editor page: title input, two-column layout (editor | summary), tip at bottom.
 * Matches EditorPage layout: centered title, editor (8 cols) | summary (4 cols) on desktop,
 * stacked on mobile; EditorSkeleton matches Editor (grid, pulse, polygon).
 */
import type { ReactNode } from "react";
import { Skeleton, Container, InputSkeleton, useDevice } from "@geometry/ui";
import { EditorSkeleton, EditorReviewSkeleton } from "@geometry/editor";

const EDITOR_SKELETON_HEIGHT = 600;
const EDITOR_COL_DESKTOP = 8;
const SUMMARY_COL_DESKTOP = 4;

export const EditorPageSkeleton = () => {
    const { isMobile } = useDevice();

    return (
        <Skeleton>
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
                    <Container padded spaced left size={isMobile ? 12 : SUMMARY_COL_DESKTOP} name="editor-summary-skeleton-col min-h-[280px]">
                        <EditorReviewSkeleton variant="requirements" />
                    </Container>
                </Container>
            </Container>
        </Skeleton>
    );
};

export const WithEditorPageSkeleton = ({ loading, children }: { loading: boolean; children: ReactNode }) =>
    loading ? <EditorPageSkeleton /> : <>{children}</>;
