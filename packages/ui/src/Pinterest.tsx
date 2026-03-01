/**
 * Pinterest-style grid layout and Pin component.
 *
 * Pin: wrapper that only accepts { children }. Used as the only allowed child type of Pinterest.
 *
 * Pinterest: validates that children are only Pin instances. Renders a 12-column grid; each Pin
 * is wrapped in a Container whose size is chosen by device and row-completion logic:
 * - isMobile: always 12 (full width).
 * - isTablet: options [6, 12]; random when starting a row.
 * - Desktop: options [3, 4, 6, 8, 9, 12]; random when starting a row.
 * Row rule: cumulative sum of sizes in a row must equal 12. When the running sum mod 12 is not 0,
 * the next size is forced to (12 - (sum % 12)) so the row completes. Example: after 9 the next is 3;
 * after 6 the next is 6; after 18 (sum%12=6) the next is 6.
 *
 * Example:
 *   <Pinterest>
 *     <Pin key="a"><Link to="/jobs/1">Job 1</Link></Pin>
 *     <Pin key="b"><Link to="/jobs/2">Job 2</Link></Pin>
 *   </Pinterest>
 */

import * as React from "react";
import { useMemo } from "react";
import { Container } from "./Container";
import { useDevice } from "./useDevice";

const DESKTOP_OPTIONS = [3, 4, 6, 8, 9, 12] as const;
const TABLET_OPTIONS = [6, 12] as const;

function pickRandom<T>(arr: readonly T[]): T {
    return arr[Math.floor(Math.random() * arr.length)];
}

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

    const sizes = useMemo(() => {
        const options = isMobile ? [12] as const : isTablet ? TABLET_OPTIONS : DESKTOP_OPTIONS;
        const out: number[] = [];
        let sum = 0;
        for (let i = 0; i < items.length; i++) {
            const remainder = sum % 12;
            const size = remainder === 0 ? pickRandom(options) : 12 - remainder;
            out.push(size);
            sum += size;
        }
        return out;
    }, [items.length, isMobile, isTablet]);

    return (
        <div className="geometry-pinterest grid grid-cols-12 w-full min-w-0 max-w-full gap-2">
            {(items as React.ReactElement<PinProps>[]).map((pin, i) => {
                const key = React.isValidElement(pin) && pin.key != null ? String(pin.key) : i;
                const size = sizes[i] ?? 12;
                return (
                    <Container key={key} name="geometry-pinterest-item" size={size} padded spaced rounded>
                        {pin.props.children}
                    </Container>
                );
            })}
        </div>
    );
};

Pinterest.displayName = "Pinterest";
