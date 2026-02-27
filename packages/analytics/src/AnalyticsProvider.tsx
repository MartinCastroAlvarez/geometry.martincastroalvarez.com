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
