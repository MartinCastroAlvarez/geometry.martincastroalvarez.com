/**
 * Theme cycle button: wraps Button, shows current theme's icon, click advances to next theme.
 * Uses THEME_VALUES and ThemeIcon from @geometry/theme; does not assume theme count or values.
 * Lives in ui to avoid theme↔ui cyclic dependency; use for theme toggle in nav.
 */
import React, { useCallback } from "react";
import { useLocale } from "@geometry/i18n";
import { THEME_VALUES, ThemeIcon, useTheme } from "@geometry/theme";
import { Button } from "./Button";

const ICON_SIZE = 14;

export const ThemeButton: React.FC = () => {
    const { t } = useLocale();
    const { theme, setTheme } = useTheme();
    const index = THEME_VALUES.indexOf(theme);
    const safeIndex = index >= 0 ? index : 0;
    const nextTheme = THEME_VALUES[(safeIndex + 1) % THEME_VALUES.length];
    const IconComponent = ThemeIcon[theme];

    const handleClick = useCallback(() => {
        setTheme(nextTheme);
    }, [nextTheme, setTheme]);

    return (
        <Button
            onClick={handleClick}
            icon={<IconComponent size={ICON_SIZE} />}
            sm
            aria-label={t(`theme.${theme}`)}
        />
    );
};
