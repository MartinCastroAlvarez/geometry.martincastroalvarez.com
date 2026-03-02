/**
 * Pinterest-style masonry layout and Pin component.
 *
 * Pin: wrapper that only accepts { children }. Optional size (pixels) is passed down to the
 * single child as height when set by Pinterest (e.g. when random=true). Used as the only
 * allowed child type of Pinterest.
 *
 * Pinterest: validates that children are only Pin instances. Renders a masonry layout using
 * CSS columns. When random=true, assigns each Pin a size via cumulative-sum formula (units
 * 4,6,8,12 only; complement to reach multiple of 12 never uses 3 or 9; on mobile unit is always 12). Root has padded
 * and spaced so Container is not required.
 *
 * Example:
 *   <Pinterest random>
 *     <Pin key="a"><Cell gallery={g} /></Pin>
 *   </Pinterest>
 */

import * as React from "react";
import { useDevice } from "./useDevice";

/** Units used when filling to a multiple of 12 (includes 4 for complement). */
const RANDOM_UNITS = [4, 6, 8, 12] as const;
/** Minimum height: when picking a new column height, use only these (8 = 200px min). */
const RANDOM_UNITS_PICK = [8, 12] as const;
const SIZE_SCALE = 25;
/** No pin is shown shorter than this (avoids tiny cards e.g. Batman, Snake). */
const MIN_PIN_HEIGHT_PX = 280;

function computeRandomSizes(count: number, isMobile: boolean): number[] {
    if (isMobile) {
        const fullHeight = 12 * SIZE_SCALE;
        return Array.from({ length: count }, () => fullHeight);
    }
    const sizes: number[] = [];
    let sum = 0;
    for (let i = 0; i < count; i++) {
        let unit: number;
        if (sum === 0 || sum % 12 === 0) {
            unit = RANDOM_UNITS_PICK[Math.floor(Math.random() * RANDOM_UNITS_PICK.length)];
        } else {
            const complement = 12 - (sum % 12);
            unit = complement === 3 ? 4 : complement === 9 ? 12 : complement;
        }
        sum += unit;
        sizes.push(Math.max(unit * SIZE_SCALE, MIN_PIN_HEIGHT_PX));
    }
    return sizes;
}

export interface PinProps {
    children?: React.ReactNode;
    /** Pixel height for the pin content; when set, passed to single child as height. Set by Pinterest when random=true. */
    size?: number;
}

export const Pin: React.FC<PinProps> = ({ children, size }: PinProps) => {
    if (size == null) return <>{children}</>;
    const child = React.Children.only(children);
    if (!React.isValidElement(child)) return <>{children}</>;
    return <>{React.cloneElement(child as React.ReactElement<{ height?: number }>, { height: size })}</>;
};

Pin.displayName = "Pin";

function isPinElement(child: React.ReactNode): child is React.ReactElement<PinProps> {
    return React.isValidElement(child) && (child.type === Pin || (child.type as { displayName?: string })?.displayName === "Pin");
}

export interface PinterestProps {
    children?: React.ReactNode;
    /** When true, assign each Pin a random size (cumulative-sum formula) and pass as size prop. Default false. */
    random?: boolean;
}

const GAP = 8;

export const Pinterest: React.FC<PinterestProps> = ({ children, random = false }: PinterestProps) => {
    const { isMobile, isTablet } = useDevice();
    const items = React.Children.toArray(children);

    const allPins = items.every(isPinElement);
    if (!allPins || items.length === 0) {
        if (items.length > 0 && !allPins) {
            console.warn("[Pinterest] Children must be Pin components only.");
        }
        return <div className="geometry-pinterest w-full min-w-0 max-w-full p-2" />;
    }

    const columnCount = isMobile ? 1 : isTablet ? 2 : 4;
    const sizes = random ? computeRandomSizes(items.length, isMobile) : null;
    const twoPinsFill = items.length === 2 && !isMobile;
    const singleRowFill = !isMobile && items.length >= 2 && items.length <= 4;

    const oneColumnWidth = `calc((100% - ${(columnCount - 1) * GAP}px) / ${columnCount})`;

    return (
        <div
            className="geometry-pinterest w-full min-w-0 max-w-full p-2 gap-2"
            style={
                twoPinsFill
                    ? {
                          display: "flex",
                          flexDirection: "row",
                          flexWrap: "nowrap",
                          gap: GAP,
                      }
                    : singleRowFill
                      ? {
                            display: "flex",
                            flexDirection: "row",
                            flexWrap: "nowrap",
                            gap: GAP,
                        }
                      : {
                            columnCount,
                            columnGap: GAP,
                            columnFill: "balance" as const,
                        }
            }
        >
            {(items as React.ReactElement<PinProps>[]).map((pin, i) => {
                const key = React.isValidElement(pin) && pin.key != null ? String(pin.key) : i;
                const size = sizes != null ? sizes[i] : undefined;
                const pinWithSize = size != null ? React.cloneElement(pin, { size }) : pin;
                const itemStyle: React.CSSProperties =
                    twoPinsFill && i === 0
                        ? { flex: `0 0 ${oneColumnWidth}`, marginBottom: GAP }
                        : twoPinsFill && i === 1
                          ? { flex: "1 1 0", minWidth: 0, marginBottom: GAP }
                          : singleRowFill
                            ? { flex: "1 1 0", minWidth: 0, marginBottom: GAP }
                            : { marginBottom: GAP };
                return (
                    <div
                        key={key}
                        className="geometry-pinterest-item break-inside-avoid rounded-xl overflow-hidden"
                        style={itemStyle}
                    >
                        {pinWithSize}
                    </div>
                );
            })}
        </div>
    );
};

Pinterest.displayName = "Pinterest";
