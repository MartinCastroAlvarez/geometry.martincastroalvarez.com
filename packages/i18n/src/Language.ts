/**
 * Supported languages for the application.
 *
 * Context: Values match locale codes used in translation JSON files (locales/en.json, locales/es.json).
 * Used by store, LocaleProvider, and getTranslations to select and load the correct locale.
 *
 * Example:
 *   import { Language } from "@repo/i18n";
 *   setLanguage(Language.ES);  // switch to Spanish
 */
export enum Language {
  EN = "EN",
  ES = "ES",
}
