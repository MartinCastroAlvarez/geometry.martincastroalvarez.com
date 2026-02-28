/**
 * Editor color from Tailwind theme (same as text-primary / bg-primary).
 *
 * Context: Konva shapes need color strings; we read --color-primary from the app's
 * index.css so Vertex and Edge share the exact same color and stay in sync with
 * Tailwind classes. No border: Vertex uses fill only (strokeWidth 0).
 */

const getVar = (name: string, fallback: string): string => {
    if (typeof document === "undefined") return fallback;
    const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
};

/** Single color for Vertex and Edge; matches Tailwind theme (--color-primary → text-primary, bg-primary). */
export const editorColors = {
    get color() {
        return getVar("--color-primary", "rgba(255, 255, 255, 0.9)");
    },
};
