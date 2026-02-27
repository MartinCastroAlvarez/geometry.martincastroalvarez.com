/**
 * Shared grid background for Editor and EditorSkeleton.
 * Dark blue background with 24px grid lines.
 */

import type { CSSProperties } from "react";

const GRID_STYLE: CSSProperties = {
    position: "absolute",
    backgroundColor: "rgba(2, 6, 23, 0.85)",
    backgroundImage: `
        linear-gradient(to right, rgba(255, 255, 255, 0.08) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.08) 1px, transparent 1px)
    `,
    backgroundSize: "24px 24px",
};

export interface GridProps {
    /** When set with height, gives the grid explicit size (e.g. Editor scroll content). */
    width?: number;
    /** When set with width, gives the grid explicit size. */
    height?: number;
    /** Additional style. */
    style?: CSSProperties;
}

export const Grid = ({ width, height, style }: GridProps) => (
    <div
        style={{
            ...GRID_STYLE,
            ...(width != null && height != null
                ? { width, height, left: 0, top: 0 }
                : { inset: 0 }),
            ...style,
        }}
    />
);
