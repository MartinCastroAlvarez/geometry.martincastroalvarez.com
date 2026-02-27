/**
 * Art gallery editor page: polygon boundary and obstacles.
 *
 * Context: Holds ArtGallery (perimeter + holes) in state; Editor from @geometry/editor
 * gets boundary and obstacles, reports changes via onChange. ResizeObserver keeps
 * editor size (width × 0.65) in sync with container. Protected by PrivateRoute.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { ArtGallery, Polygon } from "@geometry/domain";
import { Editor } from "@geometry/editor";
import { Container } from "@geometry/ui";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";

const emptyGallery = new ArtGallery(new Polygon([]));

export const EditorPage = () => {
    const editorRef = useRef<HTMLDivElement>(null);
    const [editorSize, setEditorSize] = useState({ width: 850, height: 550 });
    const [gallery, setGallery] = useState<ArtGallery>(() => emptyGallery);
    const { track } = useAnalytics();

    useEffect(() => {
        track({
            action: GoogleAnalyticsActions.EDITOR_OPEN,
            category: GoogleAnalyticsCategories.PAGE,
        });
    }, [track]);

    useEffect(() => {
        const el = editorRef.current;
        if (!el) return;
        const ro = new ResizeObserver((entries) => {
            const { width } = entries[0]?.contentRect ?? {};
            if (width != null && width > 0) {
                setEditorSize({ width, height: Math.round(width * 0.65) });
            }
        });
        ro.observe(el);
        return () => ro.disconnect();
    }, []);

    const handleChange = useCallback(
        (boundary?: Polygon, obstacles?: Polygon[]) => {
            setGallery((prev) => {
                const perimeter = boundary ?? prev.perimeter;
                const holes = obstacles ?? prev.holes;
                return new ArtGallery(perimeter, holes, prev.guards);
            });
        },
        []
    );

    return (
        <Container ref={editorRef} name="geometry-editor-wrapper w-full max-h-[70vh]" size={12}>
            <Editor
                boundary={gallery.perimeter}
                obstacles={gallery.holes}
                width={editorSize.width}
                height={editorSize.height}
                onChange={handleChange}
                readonly={false}
            />
        </Container>
    );
};
