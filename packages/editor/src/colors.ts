/**
 * Editor color palette from CSS variables with fallbacks.
 *
 * Context: getComputedStyle reads --editor-* from document.documentElement (e.g. in apps/web index.css).
 * Values are defined in the app's Tailwind @theme (--color-editor-*) and mapped to --editor-* in :root.
 * Fallbacks match the app palette when variables are not set. Used by Edge and Vertex for stroke/fill.
 *
 * Example:
 *   stroke={editorColors.vertexActive}  fill={editorColors.vertex}  stroke={editorColors.edge}
 */

/** Read editor colors from CSS variables (defined in app's index.css). Fallbacks match app @theme. */
const getVar = (name: string, fallback: string): string => {
    if (typeof document === "undefined") return fallback;
    const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
};

/** Fallbacks aligned with apps/web src/index.css @theme (--color-editor-*). */
export const editorColors = {
    get bg() {
        return getVar("--editor-bg", "rgba(2, 6, 23, 0.85)");
    },
    get border() {
        return getVar("--editor-border", "rgba(255, 255, 255, 0.12)");
    },
    get vertex() {
        return getVar("--editor-vertex", "#a3a3a3");
    },
    get vertexActive() {
        return getVar("--editor-vertex-active", "#d4d4d4");
    },
    get vertexFirst() {
        return getVar("--editor-vertex-first", "#737373");
    },
    get edge() {
        return getVar("--editor-edge", "rgba(163, 163, 163, 0.65)");
    },
    get edgeClosed() {
        return getVar("--editor-edge-closed", "#737373");
    },
    get stroke() {
        return getVar("--editor-stroke", "rgba(2, 6, 23, 0.9)");
    },
    get strokeHover() {
        return getVar("--editor-stroke-hover", "#ffffff");
    },
};
