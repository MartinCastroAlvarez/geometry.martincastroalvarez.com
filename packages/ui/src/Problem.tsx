/**
 * Problem message: danger styling with warning icon.
 *
 * Context: Similar to Badge but with danger Tailwind class. Shows a warning icon
 * (lucide-react TriangleAlert) and the given text. If children (text) is missing
 * or empty, returns null and hides.
 *
 * Example:
 *   <Problem>{errorMessage}</Problem>
 */

import React from "react";
import { TriangleAlert } from "lucide-react";

interface ProblemProps {
    /** Required; component hides when missing or empty. */
    children?: React.ReactNode;
    /** Alignment of the banner within the container; default "center". */
    align?: "left" | "center" | "right";
    /** Optional CSS class for the outer wrapper. */
    className?: string;
}

const bannerClasses = "w-full flex flex-row items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-danger-10 text-danger border border-danger";

export const Problem: React.FC<ProblemProps> = ({ children, align = "center", className }) => {
    if (children == null) return null;
    if (typeof children === "string" && children.trim() === "") return null;

    const justify =
        align === "left" ? "justify-start" : align === "right" ? "justify-end" : "justify-center";
    return (
        <div className={`geometry-problem w-full flex ${justify} ${className ?? ""}`.trim()} role="alert">
            <div className={bannerClasses}>
                <TriangleAlert className="shrink-0 size-4" aria-hidden />
                <span>{children}</span>
            </div>
        </div>
    );
};
