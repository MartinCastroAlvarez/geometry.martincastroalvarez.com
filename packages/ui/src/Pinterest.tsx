/**
 * Pinterest-style masonry layout and Pin component.
 *
 * Pin: wrapper that only accepts { children }. Used as the only allowed child type of Pinterest.
 *
 * Pinterest: validates that children are only Pin instances. Renders a masonry layout using
 * CSS columns so that elements of different height flow together (like Pinterest). Column count:
 * - isMobile: 1 column (full width).
 * - isTablet: 2 columns.
 * - Desktop: 4 columns.
 * Each Pin is wrapped in a div with break-inside: avoid so cards stay intact. Use variable-height
 * content inside each Pin (e.g. Viewer with different size) for a true masonry effect.
 *
 * Example:
 *   <Pinterest>
 *     <Pin key="a"><Link to="/gallery/1">Gallery 1</Link></Pin>
 *     <Pin key="b"><Link to="/gallery/2">Gallery 2</Link></Pin>
 *   </Pinterest>
 */

import * as React from "react";
import { useDevice } from "./useDevice";

export interface PinProps {
    children?: React.ReactNode;
}

export const Pin: React.FC<PinProps> = ({ children }: PinProps) => <>{children}</>;

Pin.displayName = "Pin";

function isPinElement(child: React.ReactNode): child is React.ReactElement<PinProps> {
    return React.isValidElement(child) && (child.type === Pin || (child.type as { displayName?: string })?.displayName === "Pin");
}

export interface PinterestProps {
    children?: React.ReactNode;
}

const GAP = 8;

export const Pinterest: React.FC<PinterestProps> = ({ children }: PinterestProps) => {
    const { isMobile, isTablet } = useDevice();
    const items = React.Children.toArray(children);

    const allPins = items.every(isPinElement);
    if (!allPins || items.length === 0) {
        if (items.length > 0 && !allPins) {
            console.warn("[Pinterest] Children must be Pin components only.");
        }
        return <div className="geometry-pinterest w-full min-w-0 max-w-full" />;
    }

    const columnCount = isMobile ? 1 : isTablet ? 2 : 4;

    return (
        <div
            className="geometry-pinterest w-full min-w-0 max-w-full"
            style={{
                columnCount,
                columnGap: GAP,
                columnFill: "balance" as const,
            }}
        >
            {(items as React.ReactElement<PinProps>[]).map((pin, i) => {
                const key = React.isValidElement(pin) && pin.key != null ? String(pin.key) : i;
                return (
                    <div
                        key={key}
                        className="geometry-pinterest-item break-inside-avoid mb-2 rounded-xl overflow-hidden"
                        style={{ marginBottom: GAP }}
                    >
                        {pin.props.children}
                    </div>
                );
            })}
        </div>
    );
};

Pinterest.displayName = "Pinterest";
