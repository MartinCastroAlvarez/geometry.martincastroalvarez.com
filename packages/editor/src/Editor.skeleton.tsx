/**
 * Skeleton for the Art Gallery Editor canvas (boundary and obstacles).
 *
 * Context: Matches Editor layout: rounded canvas with grid background as in Editor.tsx.
 * Size prop sets height only; width is 100%. Shows one polygon at center with random size and rotation.
 */

import { useMemo, type CSSProperties } from "react";
import { Grid } from "./Grid";
import { PolygonSkeleton } from "./Polygon.skeleton";

export interface EditorSkeletonProps {
    /** Sets height (px). Width is 100%. Required for layout. */
    size: number;
}

/** Base polygon size as fraction of editor height. Variation ±25% from base. */
const POLYGON_SIZE_FRACTION = 0.55;
const SIZE_VARIATION = 0.25;

function useRandomPolygon(editorHeight: number) {
    return useMemo(() => {
        const baseSize = editorHeight * POLYGON_SIZE_FRACTION;
        const variation = baseSize * SIZE_VARIATION * (2 * Math.random() - 1);
        const polygonSize = Math.max(20, baseSize + variation);
        const rotation = Math.random() * 360;
        return { size: polygonSize, rotation };
    }, [editorHeight]);
}

export const EditorSkeleton = ({ size }: EditorSkeletonProps) => {
    const height = size;
    const { size: polygonSize, rotation } = useRandomPolygon(height);

    const style: CSSProperties = {
        position: "relative",
        width: "100%",
        height,
        flexShrink: 0,
        borderRadius: 12,
        overflow: "hidden",
        border: "none",
        outline: "none",
    };

    return (
        <div role="presentation" aria-hidden style={style}>
            <Grid />
            <div
                className="animate-pulse"
                style={{
                    position: "absolute",
                    inset: 0,
                    borderRadius: 12,
                    backgroundColor: "color-mix(in srgb, var(--color-skeleton) 40%, transparent)",
                }}
            />
            <PolygonSkeleton size={polygonSize} rotation={rotation} />
        </div>
    );
};
