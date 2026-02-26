import React, { createContext, useContext, useCallback, useMemo } from "react";
import { useLocaleStore } from "./store";
import { getTranslations } from "./translations";
import { getNested, interpolate } from "./utils";
import { Language } from "./Language";

export type TFunction = (key: string, vars?: Record<string, string | number>) => string;

interface LocaleContextValue {
  language: Language;
  setLanguage: (language: Language) => void;
  t: TFunction;
}

const LocaleContext = createContext<LocaleContextValue | null>(null);

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
    [translations]
  );

  const value = useMemo(
    () => ({ language, setLanguage, t }),
    [language, setLanguage, t]
  );

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
};

export const useLocale = () => {
  const ctx = useContext(LocaleContext);
  if (!ctx) {
    throw new Error("useLocale must be used within a LocaleProvider");
  }
  return ctx;
};
