/**
 * Locale context: React context for language and translation function.
 *
 * Context: Holds the current language, setLanguage, and t(key, vars) for the app subtree.
 * LocaleProvider (LocaleProvider.tsx) supplies the value; useLocale (useLocale.ts) consumes it.
 * The context is created here and left undefined until a provider mounts. Do not put provider
 * or hook logic in this file.
 *
 * Example:
 *   import { LocaleContext } from "./LocaleContext";
 *   const value = useContext(LocaleContext);  // prefer useLocale() instead
 */

import { createContext } from "react";
import { Language } from "./Language";

export type TFunction = (key: string, vars?: Record<string, string | number>) => string;

export interface LocaleContextValue {
    language: Language;
    setLanguage: (language: Language) => void;
    t: TFunction;
}

export const LocaleContext = createContext<LocaleContextValue | null>(null);
