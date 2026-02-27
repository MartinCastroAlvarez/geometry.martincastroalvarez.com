/**
 * Shared constants for the analytics package.
 *
 * Centralizes values used by the GA provider and hook (default labels,
 * env key) so they stay in sync and are easy to change.
 */

/**
 * Default event label for tracking when no label is provided.
 * Used by track in useGoogleAnalytics.
 */
export const DEFAULT_EVENT_LABEL = "Geometry";

/**
 * Environment variable name for the Google Analytics Measurement ID (GA4).
 * The app reads this (e.g. import.meta.env.VITE_GOOGLE_TAG_ID) and passes it to
 * AnalyticsProvider as googleTagId; the package does not read env.
 */
export const GOOGLE_TAG_ID_ENV_KEY = "VITE_GOOGLE_TAG_ID";
