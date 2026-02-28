/**
 * Shared grid background for Editor and EditorSkeleton.
 * Background uses Tailwind slate classes (light: slate-200, dark: slate-900). Grid lines use
 * --grid-line from theme.css. 24px cell size.
 */

import type { CSSProperties } from "react";

/** Grid lines as linear gradients using theme variable for line color. */
const GRID_LINES =
    "linear-gradient(to right, var(--grid-line) 1px, transparent 1px), linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px)";

export interface GridProps {
    /** When set with height, gives the grid explicit size (e.g. Editor scroll content). */
    width?: number;
    /** When set with width, gives the grid explicit size. */
    height?: number;
    /** Additional style. */
    style?: CSSProperties;
}

export const Grid = ({ width, height, style }: GridProps) => {
    return (
        <div
            className="bg-slate-200 dark:bg-slate-900"
            style={{
                position: "absolute",
                pointerEvents: "none",
                backgroundImage: GRID_LINES,
                backgroundSize: "24px 24px",
                ...(width != null && height != null
                    ? { width, height, left: 0, top: 0 }
                    : { inset: 0 }),
                ...style,
            }}
        />
    );
};
