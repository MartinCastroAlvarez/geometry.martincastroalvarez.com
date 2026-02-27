/**
 * Skeleton placeholder for Input. Optional size for future use.
 *
 * Context: For search bars, form fields, etc. when data is loading.
 * No external skeleton library; uses bg-slate-500/50 animate-pulse.
 *
 * Example:
 *   {isLoading ? <InputSkeleton /> : <Input value={q} onChange={...} />}
 */

import React from "react";

export interface InputSkeletonProps {
    /** Size: sm, md (default), lg — affects height */
    sm?: boolean;
    md?: boolean;
    lg?: boolean;
    /** Width (default 100%) */
    width?: string | number;
}

const heightMap = { sm: 28, md: 32, lg: 40 };

export const InputSkeleton: React.FC<InputSkeletonProps> = ({
    sm = false,
    md: _md = true,
    lg = false,
    width = "100%",
}) => {
    const h = lg ? heightMap.lg : sm ? heightMap.sm : heightMap.md;
    const wCss = typeof width === "number" ? `${width}px` : width;

    return (
        <div
            className="rounded-lg bg-slate-500/50 animate-pulse"
            style={{ height: `${h}px`, width: wCss }}
            aria-hidden
        />
    );
};
