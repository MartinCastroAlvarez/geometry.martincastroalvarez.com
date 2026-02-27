/**
 * Public API for the analytics package: GA provider, hooks, and tracking constants.
 *
 * The app must pass the GA tag ID into the provider (e.g. from import.meta.env.VITE_GOOGLE_TAG_ID);
 * packages do not read env. Wrap with <AnalyticsProvider googleTagId={...}> and use useAnalytics() for track.
 */
export { AnalyticsProvider } from "./AnalyticsProvider";
export type { AnalyticsProviderProps } from "./AnalyticsProvider";
export { useAnalytics } from "./useAnalytics";
export { useGoogleAnalytics } from "./useGoogleAnalytics";
export { GoogleAnalyticsActions, GoogleAnalyticsCategories } from "./actions";
export { DEFAULT_EVENT_LABEL, GOOGLE_TAG_ID_ENV_KEY } from "./constants";
export type { TrackEventParams } from "./types";
export type { AnalyticsContextValue } from "./AnalyticsContext";
