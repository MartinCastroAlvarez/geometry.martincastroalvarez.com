import { useCallback, useEffect, useRef, useState } from "react";
import { ArtGallery, Polygon } from "@geometry/domain";
import { Editor } from "@geometry/editor";
import { Container } from "@geometry/ui";

const emptyGallery = new ArtGallery(new Polygon([]));

export const EditorPage = () => {
    const editorRef = useRef<HTMLDivElement>(null);
    const [editorSize, setEditorSize] = useState({ width: 850, height: 550 });
    const [gallery, setGallery] = useState<ArtGallery>(() => emptyGallery);

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
        <Container padded spaced size={12}>
            <Container size={12} center overflowVisible>
                <div ref={editorRef} className="col-span-12 w-full">
                    <Editor
                        boundary={gallery.perimeter}
                        obstacles={gallery.holes}
                        width={editorSize.width}
                        height={editorSize.height}
                        onChange={handleChange}
                        readonly={false}
                    />
                </div>
            </Container>
        </Container>
    );
};
