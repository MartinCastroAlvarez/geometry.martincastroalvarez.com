/**
 * Skeleton for Editor page: title input, canvas, toolbar.
 * WithEditorPageSkeleton shows skeleton when loading, otherwise renders children.
 */
import type { ReactNode } from "react";
import { Container, InputSkeleton } from "@geometry/ui";
import { EditorSkeleton } from "@geometry/editor";

const EDITOR_SKELETON_HEIGHT = 550;

export const EditorPageSkeleton = () => (
    <Container padded spaced size={12}>
        <Container padded spaced size={12}>
            <InputSkeleton width="100%" />
        </Container>
        <Container name="geometry-editor-wrapper w-full max-h-[70vh]" size={12}>
            <EditorSkeleton size={EDITOR_SKELETON_HEIGHT} />
        </Container>
    </Container>
);

export function WithEditorPageSkeleton({ loading, children }: { loading: boolean; children: ReactNode }) {
    return loading ? <EditorPageSkeleton /> : <>{children}</>;
}
