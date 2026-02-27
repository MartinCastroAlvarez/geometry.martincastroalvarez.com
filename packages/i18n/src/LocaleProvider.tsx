/**
 * Locale provider: supplies language, setLanguage, and t() to the tree.
 *
 * Context: Reads language from useLocaleStore (Zustand + persist), loads translations via
 * getTranslations(language), and exposes language, setLanguage, and t(key, vars) on LocaleContext.
 * t() uses dot-path keys and {{var}} interpolation (see utils). Must wrap the app (or subtree)
 * that uses useLocale().
 *
 * Example:
 *   <LocaleProvider>
 *     <App />
 *   </LocaleProvider>
 */

import React, { useCallback, useMemo } from "react";
import { LocaleContext } from "./LocaleContext";
import type { TFunction } from "./LocaleContext";
import { useLocaleStore } from "./store";
import { getTranslations } from "./translations";
import { getNested, interpolate } from "./utils";

export const LocaleProvider = ({ children }: { children: React.ReactNode }) => {
    const language = useLocaleStore((s) => s.language);
    const setLanguage = useLocaleStore((s) => s.setLanguage);
    const translations = useMemo(() => getTranslations(language), [language]);

    const t = useCallback<TFunction>(
        (key, vars) => {
            const value = getNested(translations as Record<string, unknown>, key);
            if (!value) return key;
            return vars ? interpolate(value, vars) : value;
        },
        [translations],
    );

    const value = useMemo(() => ({ language, setLanguage, t }), [language, setLanguage, t]);

    return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
};
