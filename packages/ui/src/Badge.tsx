/**
 * Status badges: danger (red), success (green), or default (neutral).
 *
 * Context: Renders a small pill-style span with variant styles. danger and success set
 * background and border; default uses bg-surface, text-primary, border-muted (reusable palette from app theme).
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
        ? "bg-danger-bg text-danger border border-danger"
        : success
          ? "bg-success-bg text-success border border-success"
          : "bg-surface text-primary border border-muted";

    return (
        <span className={`geometry-badge ${baseClasses} ${variantClasses}`.trim()}>
            {children}
        </span>
    );
};
