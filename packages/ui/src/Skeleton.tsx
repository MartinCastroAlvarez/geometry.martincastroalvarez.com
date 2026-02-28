/**
 * Skeleton layout: validtes the opacity is correct, and then displays a container with the children inside.
 * Used as the base for all app-level skeletons (apps/web/src/skeletons/*).
 */
import React, { forwardRef } from "react";
import { Container } from "./Container";

export interface SkeletonProps {
    opacity?: number;
    name?: string;
    size?: number;
    padded?: boolean;
    spaced?: boolean;
    rounded?: boolean;
    solid?: boolean;
    left?: boolean;
    center?: boolean;
    right?: boolean;
    middle?: boolean;
    bottom?: boolean;
    children?: React.ReactNode;
}

export const Skeleton = forwardRef<HTMLDivElement, SkeletonProps>(({ opacity = 60, children, ...rest }, ref) => {
    if (opacity < 0 || opacity > 100) {
        throw new Error(`Skeleton opacity must be between 0 and 100, received: ${opacity}`);
    }

    return (
        <div ref={ref} style={{ opacity: opacity / 100 }}>
            <Container {...rest}>
                {children}
            </Container>
        </div>
    );
});

Skeleton.displayName = "Skeleton";
