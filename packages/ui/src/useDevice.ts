/**
 * Device breakpoint hook: mobile / tablet / desktop from window width, updates on resize.
 *
 * Context: Uses innerWidth with breakpoints <600 = mobile, 600–899 = tablet, >=900 = desktop.
 * Resize handler is debounced (200ms) via useDebounce. SSR-safe (defaults to mobile width).
 *
 * Example:
 *   const { isMobile, isTablet, isDesktop, deviceType } = useDevice();
 *   const cols = isMobile ? 1 : 3;
 */

import { useCallback, useState, useEffect } from "react";
import { useDebounce } from "./useDebounce";

type DeviceInfo = {
    deviceType: "desktop" | "tablet" | "mobile";
    isMobile: boolean;
    isTablet: boolean;
    isDesktop: boolean;
};

const MOBILE_BREAKPOINT = 600;
const TABLET_BREAKPOINT = 1000;

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
