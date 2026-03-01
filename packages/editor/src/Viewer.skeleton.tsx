/**
 * Skeleton for the read-only Viewer (Art Gallery preview).
 *
 * Context: Matches Viewer layout: rounded canvas with grid background as in Viewer.tsx.
 * Same visual as EditorSkeleton (Grid, pulse overlay, centered polygon). Used on Jobs list
 * and gallery pages. Height prop matches Viewer; width is 100%.
 */

import { useMemo, type CSSProperties } from "react";
import { Grid } from "./Grid";
import { PolygonSkeleton } from "./Polygon.skeleton";

export interface ViewerSkeletonProps {
    /** Height of the canvas in pixels. Width is 100%. Matches Viewer height prop. */
    height: number;
}

const POLYGON_SIZE_FRACTION = 0.55;
const SIZE_VARIATION = 0.25;

const useRandomPolygon = (viewerHeight: number) => {
    return useMemo(() => {
        const baseSize = viewerHeight * POLYGON_SIZE_FRACTION;
        const variation = baseSize * SIZE_VARIATION * (2 * Math.random() - 1);
        const polygonSize = Math.max(20, baseSize + variation);
        const rotation = Math.random() * 360;
        return { size: polygonSize, rotation };
    }, [viewerHeight]);
};

export const ViewerSkeleton = ({ height }: ViewerSkeletonProps) => {
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
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
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
                    backgroundColor: "color-mix(in srgb, rgb(51 65 85) 40%, transparent)",
                }}
            />
            <PolygonSkeleton size={polygonSize} rotation={rotation} />
        </div>
    );
};
