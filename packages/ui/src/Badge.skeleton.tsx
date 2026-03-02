/**
 * Skeleton placeholder for Badge. Pill-shaped, small.
 *
 * Context: For status badges (Draft, Done, etc.) when loading.
 * No external skeleton library; uses bg-slate-700 animate-pulse.
 *
 * Example:
 *   {isLoading ? <BadgeSkeleton /> : <Badge>Draft</Badge>}
 */

import React from "react";

export interface BadgeSkeletonProps {
    /** Width (default ~3rem) */
    width?: string | number;
}

export const BadgeSkeleton: React.FC<BadgeSkeletonProps> = ({ width = "3rem" }) => {
    const wCss = typeof width === "number" ? `${width}px` : width;

    return (
        <div
            className="inline-block rounded-full bg-slate-700 animate-pulse"
            style={{ width: wCss, height: "1.25rem" }}
            aria-hidden
        />
    );
};
