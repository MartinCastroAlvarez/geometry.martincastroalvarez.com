/**
 * Absolutely positioned overlay with a centered, button-like hint box.
 * The overlay fills the given width/height and centers its content; clicks pass through.
 *
 * Example:
 *   <Tooltip width={400} height={300}>
 *     <Text center muted>Click to draw your polygon</Text>
 *   </Tooltip>
 */

import React from "react";

export interface TooltipProps {
    children: React.ReactNode;
    /** Default 0 */
    top?: number;
    /** Default 0 */
    left?: number;
    width: number;
    height: number;
    zIndex?: number;
}

export const Tooltip: React.FC<TooltipProps> = ({
    children,
    top = 0,
    left = 0,
    width,
    height,
    zIndex,
}) => {
    return (
        <div
            className="geometry-overlay"
            aria-hidden
            style={{
                position: "absolute",
                top,
                left,
                width,
                height,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                pointerEvents: "none",
                ...(zIndex != null && { zIndex }),
            }}
        >
            <div className="geometry-tooltip rounded-lg border border-white/10 bg-white/5 flex items-center justify-center">
                {children}
            </div>
        </div>
    );
};
