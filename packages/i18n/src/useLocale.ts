/**
 * useLocale hook: read language, setLanguage, and t() from locale context.
 *
 * Context: Returns the value from LocaleContext (supplied by LocaleProvider). Throws if used
 * outside LocaleProvider. Use t(key, vars) for translations with dot-path keys and {{var}}
 * interpolation; use language/setLanguage for the current Language enum and switching.
 *
 * Example:
 *   const { language, setLanguage, t } = useLocale();
 *   t("common.save");  // "Save" / "Guardar"
 *   t("greeting.hello", { name: "Jane" });  // "Hello, {{name}}" → "Hello, Jane"
 */

import { useContext } from "react";
import { LocaleContext } from "./LocaleContext";

export const useLocale = () => {
    const ctx = useContext(LocaleContext);
    if (!ctx) {
        throw new Error("useLocale must be used within a LocaleProvider");
    }
    return ctx;
};
