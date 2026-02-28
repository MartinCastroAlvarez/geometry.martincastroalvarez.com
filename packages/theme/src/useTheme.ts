/**
 * Theme hook: read current theme, setTheme, and getColor/toRgb/getVar for theme-aware colors (e.g. Konva).
 * Use in App (e.g. theme toggle): options={Object.values(Theme)}, value={theme}, onChange={setTheme}.
 * Use getColor("--color-editor-stroke") to get rgb(r,g,b) for canvas fill/stroke.
 */
import { useContext } from "react";
import { ThemeContext } from "./ThemeContext";

/** Read a CSS variable from document.documentElement (e.g. --color-editor-stroke). */
export function getVar(name: string, fallback: string): string {
    if (typeof document === "undefined") return fallback;
    const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return value || fallback;
}

/** Format space-separated "r g b" as "rgb(r, g, b)" for Konva and inline styles. */
export function toRgb(spaceSeparated: string, fallbackRgb: string): string {
    const parts = spaceSeparated.trim().split(/\s+/);
    if (parts.length !== 3) return fallbackRgb;
    const [r, g, b] = parts.map(Number);
    if (Number.isNaN(r) || Number.isNaN(g) || Number.isNaN(b)) return fallbackRgb;
    return `rgb(${r}, ${g}, ${b})`;
}

/** Get a theme color by CSS variable name; returns rgb(r,g,b) for use in Konva etc. */
export function getColor(varName: string, fallbackRgb = "rgb(0, 0, 0)"): string {
    const fallbackSpace = fallbackRgb.replace(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/, "$1 $2 $3");
    const raw = getVar(varName, fallbackSpace);
    return toRgb(raw, fallbackRgb);
}

export function useTheme() {
    const value = useContext(ThemeContext);
    if (value == null) {
        throw new Error("useTheme must be used within a ThemeProvider");
    }
    return {
        ...value,
        getColor,
        toRgb,
        getVar,
    };
}
