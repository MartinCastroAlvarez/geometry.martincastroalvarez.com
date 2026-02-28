import { useEffect, useCallback } from "react";
import { DEFAULT_EVENT_LABEL } from "./constants";
import { GoogleAnalyticsCategories } from "./actions";
import type { TrackEventParams } from "./types";

declare global {
  interface Window {
    dataLayer: unknown[];
    gtag: (...args: unknown[]) => void;
  }
}

export const injectGoogleAnalyticsScript = (tagId: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${tagId}`;

    script.onload = () => resolve();
    script.onerror = (error) => {
      const errorMsg = `Failed to load Google Analytics script for tag ID: ${tagId}`;
      console.error("❌ Script load error:", errorMsg, error);
      reject(new Error(errorMsg));
    };

    const timeoutId = setTimeout(() => {
      reject(new Error(`Google Analytics script load timeout for tag ID: ${tagId}`));
    }, 10000);

    const originalOnLoad = script.onload;
    script.onload = (event: Event) => {
      clearTimeout(timeoutId);
      if (originalOnLoad) (originalOnLoad as (e: Event) => void).call(script, event);
    };

    document.head.appendChild(script);
  });
};

/**
 * Hook that initializes GA and returns track. The tag ID is passed in by the
 * app (e.g. from import.meta.env in main.tsx); packages do not read env.
 */
export const useGoogleAnalytics = (googleTagId: string | null) => {
  const tagId = googleTagId?.trim() || null;

  useEffect(() => {
    if (!tagId || typeof window === "undefined") return;
    try {
      if (!window.dataLayer) {
        window.dataLayer = window.dataLayer || [];
        window.gtag = (...args: unknown[]) => {
          window.dataLayer.push(args);
        };
        setTimeout(() => {
          if (window.gtag) {
            window.gtag("js", new Date());
            window.gtag("config", tagId, { debug_mode: true });
          }
        }, 0);
        injectGoogleAnalyticsScript(tagId).catch((error) => {
          console.error("❌ Google Analytics setup failed:", error);
        });
      }
    } catch (error) {
      console.error("Error initializing Google Analytics:", error);
    }
  }, [tagId]);

  const track = useCallback(
    ({
      action,
      category = GoogleAnalyticsCategories.NAVIGATION,
      label = DEFAULT_EVENT_LABEL,
      value,
    }: TrackEventParams) => {
      if (!tagId) return;
      try {
        if (!window.gtag || typeof window.gtag !== "function") {
          const timeSinceLoad =
            Date.now() - (typeof window !== "undefined" && window.performance?.timing?.navigationStart || 0);
          if (timeSinceLoad > 10000) {
            console.error("❌ GA gtag not available. Event not tracked:", action);
          } else {
            console.warn("⚠️ GA still initializing, skipping event:", action);
          }
          return;
        }
        window.gtag("event", action, {
          event_category: category,
          event_label: label,
          value: value,
          custom_label: label,
          custom_category: category,
        });
      } catch (error) {
        console.error("❌ Error tracking event:", error, { action, category, label, value });
      }
    },
    [tagId],
  );

  return { track };
};
