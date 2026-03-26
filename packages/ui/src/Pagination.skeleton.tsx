/**
 * Skeleton for Pagination (prev/next controls). Matches paired Button sm layout.
 */

import React from "react";
import { ButtonSkeleton } from "./Button.skeleton";

export interface PaginationSkeletonProps {
    className?: string;
}

export const PaginationSkeleton: React.FC<PaginationSkeletonProps> = ({ className = "" }) => (
    <div
        className={`flex flex-row items-center justify-center gap-2 py-4 ${className}`.trim()}
        aria-hidden
    >
        <ButtonSkeleton sm />
        <ButtonSkeleton sm />
    </div>
);

PaginationSkeleton.displayName = "PaginationSkeleton";
