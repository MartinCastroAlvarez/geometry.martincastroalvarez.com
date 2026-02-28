/**
 * Theme context: holds current theme and setTheme from ThemeProvider.
 * useTheme() reads from this context. Do not put provider logic here.
 */
import { createContext } from "react";
import type { Theme } from "./Theme";

export type ThemeContextValue = {
    theme: Theme;
    setTheme: (next: Theme | ((prev: Theme) => Theme)) => void;
};

export const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);
