/**
 * Shared constants for the i18n package.
 *
 * Centralizes keys and values used across store, provider, and any persistence
 * so they stay in sync and are easy to change (e.g. for namespacing or migration).
 */

/**
 * Key under which the persisted locale state is stored in localStorage.
 * Used by the Zustand persist middleware in the locale store so the selected
 * language survives page reloads and is consistent across tabs.
 */
export const LOCALE_STORAGE_KEY = "geometry-locale";
