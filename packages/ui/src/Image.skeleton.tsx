/**
 * Skeleton placeholder for Image. Matches Image size and rounded style.
 *
 * Context: Used by Nav.skeleton for avatar and by cards/lists for image placeholders.
 * No external skeleton library; uses bg-slate-700 animate-pulse.
 *
 * Example:
 *   {isLoading ? <ImageSkeleton size={28} rounded /> : <Image src={url} size={28} rounded />}
 */

import React from "react";

export interface ImageSkeletonProps {
    /** Size in px (default 24, matches Logo small) */
    size?: number;
    /** Circular when true (default true for avatars) */
    rounded?: boolean;
}

export const ImageSkeleton: React.FC<ImageSkeletonProps> = ({ size = 24, rounded = true }) => {
    return (
        <div
            className={`shrink-0 bg-slate-700 animate-pulse ${rounded ? "rounded-full" : "rounded-lg"}`}
            style={{ width: size, height: size }}
            aria-hidden
        />
    );
};
