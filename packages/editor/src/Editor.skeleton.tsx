/**
 * Skeleton for the Art Gallery Editor canvas (boundary and obstacles).
 *
 * Context: Matches Editor layout: rounded canvas with grid background as in Editor.tsx.
 * ArtGallery (api/models/gallery.py) has boundary, obstacles, ears, convex_components, guards, visibility;
 * the editor edits boundary and obstacles. This skeleton mirrors the canvas area only.
 * Uses animate-pulse; no external skeleton library (same approach as time app).
 */

export interface EditorSkeletonProps {
    width?: number;
    height?: number;
}

const DEFAULT_WIDTH = 850;
const DEFAULT_HEIGHT = 550;

export const EditorSkeleton = ({ width = DEFAULT_WIDTH, height = DEFAULT_HEIGHT }: EditorSkeletonProps) => {
    return (
        <div
            role="presentation"
            aria-hidden
            style={{
                position: "relative",
                width,
                height,
                minWidth: width,
                minHeight: height,
                flexShrink: 0,
                borderRadius: 12,
                overflow: "hidden",
            }}
        >
            <div
                style={{
                    position: "absolute",
                    inset: 0,
                    backgroundColor: "rgba(2, 6, 23, 0.85)",
                    backgroundImage: `
                        linear-gradient(to right, rgba(255, 255, 255, 0.08) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(255, 255, 255, 0.08) 1px, transparent 1px)
                    `,
                    backgroundSize: "24px 24px",
                }}
            />
            <div
                className="animate-pulse"
                style={{
                    position: "absolute",
                    inset: 8,
                    borderRadius: 8,
                    backgroundColor: "rgba(148, 163, 184, 0.2)",
                }}
            />
        </div>
    );
};
