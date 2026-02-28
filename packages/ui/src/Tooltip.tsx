/**
 * Absolutely positioned overlay with a hint box. The overlay fills the given width/height.
 * Children are rendered inside Text (center, muted). Use boolean props to position the box
 * inside the overlay: top, bottom, left, right. If none are set, the box is centered.
 * Clicks pass through.
 *
 * Example:
 *   <Tooltip width={400} height={300}>Click to draw your polygon</Tooltip>
 *   <Tooltip width={400} height={300} right bottom>Close the polygon to continue</Tooltip>
 */

import React from "react";
import { Text } from "./Text";

export interface TooltipProps {
    children: React.ReactNode;
    /** Overlay offset from top (default 0) */
    overlayTop?: number;
    /** Overlay offset from left (default 0) */
    overlayLeft?: number;
    width: number;
    height: number;
    z?: number;
    /** Position the tooltip box at the top of the overlay */
    top?: boolean;
    /** Position the tooltip box at the bottom of the overlay */
    bottom?: boolean;
    /** Position the tooltip box at the left of the overlay */
    left?: boolean;
    /** Position the tooltip box at the right of the overlay */
    right?: boolean;
}

export const Tooltip: React.FC<TooltipProps> = ({
    children,
    overlayTop = 0,
    overlayLeft = 0,
    width,
    height,
    z,
    top = false,
    bottom = false,
    left = false,
    right = false,
}) => {
    const alignItems = top ? "flex-start" : bottom ? "flex-end" : "center";
    const justifyContent = left ? "flex-start" : right ? "flex-end" : "center";

    return (
        <div
            className="geometry-overlay"
            aria-hidden
            style={{
                position: "absolute",
                top: overlayTop,
                left: overlayLeft,
                width,
                height,
                padding: "0.5rem",
                display: "flex",
                alignItems,
                justifyContent,
                pointerEvents: "none",
                ...(z != null && { zIndex: z }),
            }}
        >
            <div className="geometry-tooltip rounded-lg border-0 flex items-center justify-center p-3">
                <Text center muted xs>
                    {children}
                </Text>
            </div>
        </div>
    );
};
