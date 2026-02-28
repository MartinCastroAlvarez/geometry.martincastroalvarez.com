/**
 * Skeleton placeholder for Button. Matches Button layout (pill-shaped, with optional size).
 *
 * Context: Used by Nav.skeleton and anywhere a button is shown while loading.
 * No external skeleton library; uses bg-skeleton animate-pulse.
 *
 * Example:
 *   {isLoading ? <ButtonSkeleton sm /> : <Button sm>Create</Button>}
 */

import React from "react";

export interface ButtonSkeletonProps {
    /** Size variant matching Button: xs, sm (default), lg */
    xs?: boolean;
    sm?: boolean;
    lg?: boolean;
    /** Optional fixed width (e.g. "4rem") */
    width?: string | number;
    /** Optional fixed height (e.g. "2rem") */
    height?: string | number;
}

const sizeMap = {
    xs: { w: 48, h: 24 },
    sm: { w: 72, h: 28 },
    lg: { w: 96, h: 32 },
};

export const ButtonSkeleton: React.FC<ButtonSkeletonProps> = ({
    xs = false,
    sm: _sm = true,
    lg = false,
    width,
    height,
}) => {
    const size = lg ? "lg" : xs ? "xs" : "sm";
    const { w, h } = sizeMap[size];
    const wVal = width ?? `${w}px`;
    const hVal = height ?? `${h}px`;
    const wCss = typeof wVal === "number" ? `${wVal}px` : wVal;
    const hCss = typeof hVal === "number" ? `${hVal}px` : hVal;

    return (
        <div
            className="rounded-lg bg-skeleton animate-pulse shrink-0"
            style={{ width: wCss, height: hCss }}
            aria-hidden
        />
    );
};
