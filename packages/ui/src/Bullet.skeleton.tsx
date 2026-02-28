/**
 * Skeleton placeholder for Bullet. Matches Bullet layout: icon column (w-5, one line height) + text.
 * Used by EditorPage summary skeleton (requirements variant) so loading state matches the requirements list.
 */

import React from "react";
import { TextSkeleton } from "./Text.skeleton";

export interface BulletSkeletonProps {
    /** Size variant for the text line; matches Bullet sm by default. */
    sm?: boolean;
    /** Width of the text line (e.g. "85%" or "70%") for variety in lists. */
    width?: string | number;
}

export const BulletSkeleton: React.FC<BulletSkeletonProps> = ({ sm = true, width }) => {
    return (
        <div className="geometry-bullet-skeleton flex gap-2 items-start w-full" aria-hidden>
            <span className="shrink-0 w-5 h-[1.25em] flex items-center justify-center">
                <span className="w-4 h-4 rounded-full bg-skeleton animate-pulse" />
            </span>
            <div className="flex-1 min-w-0">
                <TextSkeleton sm={sm} width={width ?? "90%"} lines={1} />
            </div>
        </div>
    );
};
