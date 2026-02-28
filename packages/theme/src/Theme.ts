/**
 * Theme enum: available theme identifiers.
 * Add entries here and add [data-theme="<value>"] in theme.css to support more themes.
 */
export const Theme = {
    Dark: "dark",
    Light: "light",
} as const;

export type Theme = (typeof Theme)[keyof typeof Theme];

export const THEME_VALUES: Theme[] = Object.values(Theme);

export function isTheme(value: string | null): value is Theme {
    return value != null && THEME_VALUES.includes(value as Theme);
}
