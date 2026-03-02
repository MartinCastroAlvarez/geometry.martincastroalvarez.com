/**
 * Theme icons: one icon per theme value, same keys as Theme.
 * Used by ThemeButton to show the current theme's icon. Light = Sun, Dark = Moon.
 */
import type { LucideIcon } from "lucide-react";
import { Moon, Sun } from "lucide-react";
import { Theme } from "./Theme";

/** Map each theme value to its icon component. Same size/keys as Theme. */
export const ThemeIcon: Record<Theme, LucideIcon> = {
    [Theme.Dark]: Moon,
    [Theme.Light]: Sun,
} as const;
