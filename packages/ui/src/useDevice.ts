import { useCallback, useState, useEffect } from "react";
import { useDebounce } from "./useDebounce";

type DeviceInfo = {
    deviceType: "desktop" | "tablet" | "mobile";
    isMobile: boolean;
    isTablet: boolean;
    isDesktop: boolean;
};

const MOBILE_BREAKPOINT = 600;
const TABLET_BREAKPOINT = 900;

/**
 * useDevice Hook
 *
 * Determines if the current device is 'mobile', 'tablet', or 'desktop' based on window width.
 * Dynamically updates on window resize events.
 *
 * Breakpoints:
 * - Mobile: < 600px
 * - Tablet: 600px - 899px
 * - Desktop: >= 900px
 */
export const useDevice = (): DeviceInfo => {
    const [width, setWidth] = useState(typeof window !== "undefined" ? window.innerWidth : MOBILE_BREAKPOINT);

    const setWidthFromWindow = useCallback(() => setWidth(window.innerWidth), []);
    const handleResize = useDebounce(setWidthFromWindow, 200);

    useEffect(() => {
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [handleResize]);

    const isMobile = width < MOBILE_BREAKPOINT;
    const isTablet = width >= MOBILE_BREAKPOINT && width < TABLET_BREAKPOINT;
    const isDesktop = width >= TABLET_BREAKPOINT;

    const deviceType: "mobile" | "tablet" | "desktop" = isMobile ? "mobile" : isTablet ? "tablet" : "desktop";

    return { deviceType, isMobile, isTablet, isDesktop };
};
