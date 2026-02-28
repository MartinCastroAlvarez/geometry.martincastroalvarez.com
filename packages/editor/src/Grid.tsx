/**
 * Shared grid background for Editor and EditorSkeleton.
 * Background uses Tailwind slate classes (light: slate-200, dark: slate-900). Grid lines use
 * --grid-line from theme.css. cell prop (default 24px).
 */

/** Grid lines as linear gradients using theme variable for line color. */
const GRID_LINES =
    "linear-gradient(to right, var(--grid-line) 1px, transparent 1px), linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px)";

export interface GridProps {
    /** When set with height, gives the grid explicit size (e.g. Editor scroll content). */
    width?: number;
    /** When set with width, gives the grid explicit size. */
    height?: number;
    /** Grid cell size in pixels (default 24). */
    cell?: number;
}

const DEFAULT_CELL = 18;

export const Grid = ({ width, height, cell = DEFAULT_CELL }: GridProps) => (
    <div
        className="bg-slate-200 dark:bg-slate-900 absolute inset-0 pointer-events-none z-0 opacity-40"
        style={{
            backgroundImage: GRID_LINES,
            backgroundSize: `${cell}px ${cell}px`,
            ...(width != null && height != null ? { width, height, left: 0, top: 0 } : {}),
        }}
    />
);
