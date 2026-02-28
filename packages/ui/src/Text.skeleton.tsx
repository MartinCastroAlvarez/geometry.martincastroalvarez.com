/**
 * Skeleton placeholder for Text. Matches Text size variants.
 *
 * Context: Used by Nav.skeleton (e.g. "Jobs", "Logout", user name) and list/grid placeholders.
 * No external skeleton library; uses bg-skeleton animate-pulse.
 *
 * Example:
 *   {isLoading ? <TextSkeleton sm /> : <Text sm>Content</Text>}
 */

import React from "react";

export interface TextSkeletonProps {
    /** Size variant matching Text: xs, sm, md, lg, xl, xxl, xxxl */
    xs?: boolean;
    sm?: boolean;
    md?: boolean;
    lg?: boolean;
    xl?: boolean;
    xxl?: boolean;
    xxxl?: boolean;
    /** Number of lines (default 1) */
    lines?: number;
    /** Width as CSS value or number of px (default from size). Use e.g. "3rem" or 80 */
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

export const TextSkeleton: React.FC<TextSkeletonProps> = ({
    xs = false,
    sm = false,
    md = false,
    lg = false,
    xl = false,
    xxl = false,
    xxxl = false,
    lines = 1,
    width,
}) => {
    const sizeKey = xxxl ? "xxxl" : xxl ? "xxl" : xl ? "xl" : lg ? "lg" : md ? "md" : sm ? "sm" : xs ? "xs" : "md";
    const lineHeight = sizeHeightMap[sizeKey] ?? 16;
    const widthCss = width == null ? "100%" : typeof width === "number" ? `${width}px` : width;

    return (
        <div className="flex flex-col gap-1.5" aria-hidden>
            {Array.from({ length: lines }).map((_, i) => (
                <div
                    key={i}
                    className="rounded bg-skeleton animate-pulse"
                    style={{
                        height: `${lineHeight}px`,
                        width: lines === 1 ? widthCss : i === lines - 1 && lines > 1 ? "75%" : widthCss,
                    }}
                />
            ))}
        </div>
    );
};
