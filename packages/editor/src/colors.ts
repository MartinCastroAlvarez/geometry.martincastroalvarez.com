/** Read editor colors from CSS variables (defined in app's index.css). Fallbacks match app palette. */
const getVar = (name: string, fallback: string): string => {
    if (typeof document === "undefined") return fallback;
    const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
};

export const editorColors = {
    get bg() {
        return getVar("--editor-bg", "rgba(26, 26, 26, 0.6)");
    },
    get border() {
        return getVar("--editor-border", "rgba(100, 116, 139, 0.5)");
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
        return getVar("--editor-stroke", "#1a1a1a");
    },
    get strokeHover() {
        return getVar("--editor-stroke-hover", "#ffffff");
    },
};
