/** Read editor colors from CSS variables (defined in app's index.css). Fallbacks match app palette. */
function getVar(name: string, fallback: string): string {
    if (typeof document === "undefined") return fallback;
    const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
}

export const editorColors = {
    get bg() {
        return getVar("--editor-bg", "rgba(26, 26, 26, 0.6)");
    },
    get border() {
        return getVar("--editor-border", "rgba(100, 116, 139, 0.5)");
    },
    get vertex() {
        return getVar("--editor-vertex", "#0f62fe");
    },
    get vertexActive() {
        return getVar("--editor-vertex-active", "#f59e0b");
    },
    get vertexFirst() {
        return getVar("--editor-vertex-first", "#22c55e");
    },
    get edge() {
        return getVar("--editor-edge", "#64748b");
    },
    get edgeClosed() {
        return getVar("--editor-edge-closed", "#22c55e");
    },
    get stroke() {
        return getVar("--editor-stroke", "#1a1a1a");
    },
    get strokeHover() {
        return getVar("--editor-stroke-hover", "#ffffff");
    },
};
