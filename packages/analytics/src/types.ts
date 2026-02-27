import type { GoogleAnalyticsActions, GoogleAnalyticsCategories } from "./actions";

export interface TrackEventParams {
  action: GoogleAnalyticsActions;
  category?: GoogleAnalyticsCategories;
  label?: string;
  value?: number;
}
