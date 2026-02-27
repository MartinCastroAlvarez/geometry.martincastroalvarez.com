/**
 * Translation resources and loader by language.
 *
 * Context: Maps Language enum to locale JSON (en.json, es.json). getTranslations(language) returns the full
 * nested translation object for that language; falls back to EN if unknown. Type Translations = typeof en.
 *
 * Example:
 *   const tr = getTranslations(Language.ES);
 *   tr.common.cancel;  // "Cancelar"
 */
import en from "./locales/en.json";
import es from "./locales/es.json";
import { Language } from "./Language";

export type Translations = typeof en;

const resources: Record<Language, Translations> = {
  [Language.EN]: en,
  [Language.ES]: es,
};

export const getTranslations = (language: Language): Translations =>
  resources[language] ?? resources[Language.EN];
