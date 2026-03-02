/**
 * Language cycle button: wraps Button, shows current language code (e.g. EN, ES), click advances to next.
 * Uses Language enum values; does not assume count or values. No icon; label is the language code.
 */
import React, { useCallback } from "react";
import { Language, useLocale } from "@geometry/i18n";
import { Button } from "./Button";

const LANGUAGE_VALUES: Language[] = Object.values(Language);

export const LanguageButton: React.FC = () => {
    const { language, setLanguage } = useLocale();
    const index = LANGUAGE_VALUES.indexOf(language);
    const safeIndex = index >= 0 ? index : 0;
    const nextLanguage = LANGUAGE_VALUES[(safeIndex + 1) % LANGUAGE_VALUES.length];

    const handleClick = useCallback(() => {
        setLanguage(nextLanguage);
    }, [nextLanguage, setLanguage]);

    return (
        <Button onClick={handleClick} sm aria-label={language}>
            {language}
        </Button>
    );
};
