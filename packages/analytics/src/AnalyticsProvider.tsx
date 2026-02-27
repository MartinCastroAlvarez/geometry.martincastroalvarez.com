/**
 * Analytics provider: supplies GA tag ID and track() to the tree.
 *
 * Context: Accepts googleTagId (from app env, e.g. import.meta.env.VITE_GOOGLE_TAG_ID) and
 * uses useGoogleAnalytics to inject the gtag script and build the track function. Provides
 * { googleTagId, track } on AnalyticsContext. Packages do not read env; the app must pass
 * the tag ID. Wrap the app (or subtree) that uses useAnalytics().
 *
 * Example:
 *   <AnalyticsProvider googleTagId={import.meta.env.VITE_GOOGLE_TAG_ID ?? null}>
 *     <App />
 *   </AnalyticsProvider>
 */

import { ReactNode } from "react";
import { AnalyticsContext } from "./AnalyticsContext";
import { useGoogleAnalytics } from "./useGoogleAnalytics";

export interface AnalyticsProviderProps {
    children: ReactNode;
    /** Google Analytics Measurement ID (GA4). Set by the app from env (e.g. import.meta.env.VITE_GOOGLE_TAG_ID). Pass null to disable. */
    googleTagId: string | null;
}

export const AnalyticsProvider = ({ children, googleTagId }: AnalyticsProviderProps) => {
    const { track } = useGoogleAnalytics(googleTagId);
    return (
        <AnalyticsContext.Provider value={{ googleTagId: googleTagId?.trim() || null, track }}>
            {children}
        </AnalyticsContext.Provider>
    );
};
