import { create } from "zustand";
import { persist } from "zustand/middleware";
import { Language } from "./Language";

const STORAGE_KEY = "geometry-locale";

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
    { name: STORAGE_KEY, partialize: (s) => ({ language: s.language }) }
  )
);
