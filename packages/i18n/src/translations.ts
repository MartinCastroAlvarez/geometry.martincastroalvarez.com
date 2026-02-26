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
