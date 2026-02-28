/**
 * Skeleton layout: validtes the opacity is correct, and then displays a container with the children inside.
 * Used as the base for all app-level skeletons (apps/web/src/skeletons/*).
 */
import { forwardRef, type ReactNode } from "react";

export interface SkeletonProps {
    opacity?: number;
    children?: ReactNode;
}

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(({ opacity = 60, children }, ref) => {
    if (opacity < 0 || opacity > 100) {
        throw new Error(`Skeleton opacity must be between 0 and 100, received: ${opacity}`);
    }

    return (
        <div ref={ref} className={`opacity-${opacity} w-full h-full animate-pulse`}>
            {children}
        </div>
    );
});

Skeleton.displayName = "Skeleton";
