/**
 * Status badges: danger (red), success (green), or default (neutral).
 *
 * Context: Renders a small pill-style span with variant styles. danger and success set
 * background and border; default is white/10 with white/80 text.
 *
 * Example:
 *   <Badge>Draft</Badge>
 *   <Badge danger>Failed</Badge>
 *   <Badge success>Done</Badge>
 */

import React from "react";

interface BadgeProps {
    children: React.ReactNode;
    danger?: boolean;
    success?: boolean;
}

const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";

export const Badge: React.FC<BadgeProps> = ({ children, danger = false, success = false }) => {
    const variantClasses = danger
        ? "bg-red-500/20 text-red-300 border border-red-500/40"
        : success
          ? "bg-green-500/20 text-green-300 border border-green-500/40"
          : "bg-white/10 text-white/80 border border-white/20";

    return (
        <span className={`geometry-badge ${baseClasses} ${variantClasses}`.trim()}>
            {children}
        </span>
    );
};
