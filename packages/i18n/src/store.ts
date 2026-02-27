/**
 * Persisted locale store: current language and setter.
 *
 * Context: Zustand store with persist middleware; key from LOCALE_STORAGE_KEY in localStorage.
 * Holds language (Language enum) and setLanguage. LocaleProvider subscribes and passes value + t() to context.
 *
 * Example:
 *   const language = useLocaleStore((s) => s.language);
 *   const setLanguage = useLocaleStore((s) => s.setLanguage);
 *   setLanguage(Language.ES);
 */
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Language } from "./Language";
import { LOCALE_STORAGE_KEY } from "./constants";

interface LocaleState {
  language: Language;
  setLanguage: (language: Language) => void;
}

export const useLocaleStore = create<LocaleState>()(
  persist(
    (set) => ({
      language: Language.EN,
      setLanguage: (language) => set({ language }),
    }),
    { name: LOCALE_STORAGE_KEY, partialize: (s) => ({ language: s.language }) }
  )
);
