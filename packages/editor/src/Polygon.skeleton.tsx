/**
 * Skeleton polygon: a single square with given size and rotation (0–360).
 * Used by Editor.skeleton to show one centered placeholder.
 */

export interface PolygonSkeletonProps {
    /** Side length of the square in px. */
    size: number;
    /** Rotation in degrees, 0–360. */
    rotation: number;
}

export const PolygonSkeleton = ({ size, rotation }: PolygonSkeletonProps) => (
    <div
        className="animate-pulse"
        role="presentation"
        aria-hidden
        style={{
            position: "relative",
            width: size,
            height: size,
            borderRadius: 6,
            backgroundColor: "color-mix(in srgb, rgb(51 65 85) 45%, transparent)",
            transform: `rotate(${rotation}deg)`,
            transformOrigin: "center",
        }}
    />
);
