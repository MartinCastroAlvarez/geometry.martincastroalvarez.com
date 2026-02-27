/**
 * Public API for the i18n package: locale state, provider, and translation loading.
 *
 * Context: Re-exports Language enum, LocaleProvider/useLocale (React context), useLocaleStore (Zustand + persist),
 * getTranslations (locale → JSON), and TFunction type. App should wrap with LocaleProvider and use useLocale() or useLocaleStore().
 *
 * Example:
 *   import { LocaleProvider, useLocale, Language } from "@repo/i18n";
 *   <LocaleProvider><App /></LocaleProvider>
 *   const { t, language, setLanguage } = useLocale();
 */
export { Language } from "./Language";
export { LocaleProvider, useLocale } from "./LocaleProvider";
export type { TFunction } from "./LocaleProvider";
export { useLocaleStore } from "./store";
export { getTranslations } from "./translations";
