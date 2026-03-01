/**
 * Skeleton placeholder for Inspector. Matches the scrollable JSON view area.
 *
 * Context: Used by JobPage.skeleton when loading job detail. Uses a fixed height
 * to match Inspector size prop.
 */

import React from "react";

export interface InspectorSkeletonProps {
    /** Height in pixels to match Inspector size. Default 300. */
    size?: number;
}

export const InspectorSkeleton: React.FC<InspectorSkeletonProps> = ({ size = 300 }) => {
    return (
        <div
            className="rounded bg-slate-700 animate-pulse w-full overflow-hidden"
            style={{ height: `${size}px` }}
            aria-hidden
        />
    );
};
