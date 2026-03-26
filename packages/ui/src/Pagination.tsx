/**
 * Cursor-based prev/next pagination (no total count or last page).
 *
 * Context: For APIs that return `next_token` only. Parent keeps a token trail and passes
 * canGoPrevious / canGoNext from the current cursor and response.
 */

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useLocale } from "@geometry/i18n";
import { Button } from "./Button";
import { PaginationSkeleton } from "./Pagination.skeleton";

export interface PaginationProps {
    /** True when not on the first page (cursor > 0). */
    canGoPrevious: boolean;
    /** True when the last response included a non-empty next_token. */
    canGoNext: boolean;
    onPrevious: () => void;
    onNext: () => void;
    /** Disable both controls (e.g. while a request is in flight). */
    disabled?: boolean;
    /** When true, renders PaginationSkeleton instead of buttons. */
    loading?: boolean;
    className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
    canGoPrevious,
    canGoNext,
    onPrevious,
    onNext,
    disabled = false,
    loading = false,
    className = "",
}) => {
    const { t } = useLocale();

    if (loading) {
        return <PaginationSkeleton className={className} />;
    }

    if (!canGoPrevious && !canGoNext) {
        return null;
    }

    return (
        <div className={`flex flex-row items-center justify-center gap-2 py-4 ${className}`.trim()}>
            <Button
                sm
                icon={<ChevronLeft size={18} aria-hidden />}
                disabled={disabled || !canGoPrevious}
                onClick={onPrevious}
                aria-label={t("common.previousPage")}
            />
            <Button
                sm
                icon={<ChevronRight size={18} aria-hidden />}
                disabled={disabled || !canGoNext}
                onClick={onNext}
                aria-label={t("common.nextPage")}
            />
        </div>
    );
};

Pagination.displayName = "Pagination";
