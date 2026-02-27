import { createContext } from "react";
import type { TrackEventParams } from "./types";

export interface AnalyticsContextValue {
  googleTagId: string | null;
  track: (params: TrackEventParams) => void;
}

export const AnalyticsContext = createContext<AnalyticsContextValue | undefined>(undefined);
