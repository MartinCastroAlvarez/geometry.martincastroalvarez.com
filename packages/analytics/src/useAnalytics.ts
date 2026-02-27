/**
 * useAnalytics hook: read googleTagId and track() from analytics context.
 *
 * Context: Returns the value from AnalyticsContext (supplied by AnalyticsProvider). Throws if
 * used outside AnalyticsProvider. Use track({ action, category?, label?, value? }) to send
 * events to GA4. Use GoogleAnalyticsActions and GoogleAnalyticsCategories from actions for
 * consistent names.
 *
 * Example:
 *   const { track } = useAnalytics();
 *   track({ action: GoogleAnalyticsActions.PAGE_VIEW, label: "/jobs" });
 */

import { useContext } from "react";
import { AnalyticsContext } from "./AnalyticsContext";

export const useAnalytics = () => {
    const context = useContext(AnalyticsContext);
    if (context === undefined) {
        throw new Error("useAnalytics must be used within an AnalyticsProvider");
    }
    return context;
};
