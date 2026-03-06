/**
 * Shared grid background for Editor and Viewer.
 * Solid background at full opacity (light: slate-200, dark: slate-900); grid lines at reduced
 * opacity so the canvas has a visible background. size prop (default 18px).
 */

/** Grid lines as linear gradients using theme variable for line color. */
const GRID_LINES =
    "linear-gradient(to right, var(--grid-line) 1px, transparent 1px), linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px)";

export interface GridProps {
    /** When set with height, gives the grid explicit size (e.g. Editor scroll content). */
    width?: number;
    /** When set with width, gives the grid explicit size. */
    height?: number;
    /** Grid cell size in pixels (default 18). */
    size?: number;
    /** Grid line opacity 0–100 (default 20). Background is always full opacity. */
    opacity?: number;
}

const DEFAULT_SIZE = 18;
const DEFAULT_OPACITY = 20;

export const Grid = ({ width, height, size = DEFAULT_SIZE, opacity = DEFAULT_OPACITY }: GridProps) => {
    let resolvedOpacity = DEFAULT_OPACITY;
    if (typeof opacity === "number" && Number.isFinite(opacity) && opacity >= 0 && opacity <= 100) {
        resolvedOpacity = opacity;
    }
    const sizeStyle = width != null && height != null ? { width, height, left: 0, top: 0 } : {};
    return (
        <div
            className="absolute inset-0 pointer-events-none z-0"
            style={{
                ...sizeStyle,
                background: "rgb(var(--color-canvas-bg))",
            }}
        >
            <div
                aria-hidden
                className="absolute inset-0 pointer-events-none"
                style={{
                    backgroundImage: GRID_LINES,
                    backgroundSize: `${size}px ${size}px`,
                    opacity: resolvedOpacity / 100,
                    ...sizeStyle,
                }}
            />
        </div>
    );
};
