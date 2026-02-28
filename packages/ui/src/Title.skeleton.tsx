/**
 * Skeleton placeholder for Title. Matches Title size variants.
 *
 * Context: Used by Nav.skeleton for "Art Gallery" title and other headings.
 * No external skeleton library; uses bg-slate-700 animate-pulse.
 *
 * Example:
 *   {isLoading ? <TitleSkeleton lg /> : <Title lg>Art Gallery</Title>}
 */

import React from "react";

export interface TitleSkeletonProps {
    /** Size variant matching Title: xs, sm, md, lg, xl, xxl, xxxl */
    xs?: boolean;
    sm?: boolean;
    md?: boolean;
    lg?: boolean;
    xl?: boolean;
    xxl?: boolean;
    xxxl?: boolean;
    /** Width as CSS value or number of px */
    width?: string | number;
}

const sizeHeightMap: Record<string, number> = {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    xxxl: 30,
};

export const TitleSkeleton: React.FC<TitleSkeletonProps> = ({
    xs = false,
    sm = false,
    md = false,
    lg = false,
    xl = false,
    xxl = false,
    xxxl = false,
    width,
}) => {
    const sizeKey = xxxl ? "xxxl" : xxl ? "xxl" : xl ? "xl" : lg ? "lg" : md ? "md" : sm ? "sm" : xs ? "xs" : "lg";
    const lineHeight = sizeHeightMap[sizeKey] ?? 18;
    const widthCss = width == null ? "6rem" : typeof width === "number" ? `${width}px` : width;

    return (
        <div
            className="rounded bg-slate-700 animate-pulse shrink-0"
            style={{ height: `${lineHeight}px`, width: widthCss }}
            aria-hidden
        />
    );
};
