/**
 * Theme provider: holds current theme, persists to localStorage, sets data-theme on documentElement.
 * Wrap the app (or subtree) that uses useTheme(). No props required; theme is read from localStorage on init.
 */
import React, { useCallback, useEffect, useState } from "react";
import type { ThemeContextValue } from "./ThemeContext";
import { ThemeContext } from "./ThemeContext";
import { Theme, isTheme } from "./Theme";

const THEME_KEY = "theme";

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [theme, setThemeState] = useState<Theme>(() => {
        if (typeof document === "undefined") return Theme.Dark;
        const stored = localStorage.getItem(THEME_KEY);
        return isTheme(stored) ? stored : Theme.Dark;
    });

    if (typeof document !== "undefined") {
        document.documentElement.setAttribute("data-theme", theme);
    }

    useEffect(() => {
        localStorage.setItem(THEME_KEY, theme);
    }, [theme]);

    useEffect(() => {
        const stored = localStorage.getItem(THEME_KEY);
        if (isTheme(stored)) {
            document.documentElement.setAttribute("data-theme", stored);
            setThemeState(stored);
        }
    }, []);

    const setTheme = useCallback((next: Theme | ((prev: Theme) => Theme)) => {
        setThemeState((prev) => (typeof next === "function" ? next(prev) : next));
    }, []);

    const value: ThemeContextValue = { theme, setTheme };
    return (
        <ThemeContext.Provider value={value}>
            {children}
        </ThemeContext.Provider>
    );
};
