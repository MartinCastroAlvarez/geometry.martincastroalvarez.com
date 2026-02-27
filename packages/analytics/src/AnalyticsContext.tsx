/**
 * Analytics context: React context for GA tag ID and track function.
 *
 * Context: Holds googleTagId (GA4 Measurement ID) and track(params) for the app subtree.
 * AnalyticsProvider (AnalyticsProvider.tsx) supplies the value; useAnalytics (useAnalytics.ts)
 * consumes it. The context is created here and left undefined until a provider mounts. Do not
 * put provider or hook logic in this file.
 *
 * Example:
 *   import { AnalyticsContext } from "./AnalyticsContext";
 *   const value = useContext(AnalyticsContext);  // prefer useAnalytics() instead
 */

import { createContext } from "react";
import type { TrackEventParams } from "./types";

export interface AnalyticsContextValue {
    googleTagId: string | null;
    track: (params: TrackEventParams) => void;
}

export const AnalyticsContext = createContext<AnalyticsContextValue | undefined>(undefined);
