/**
 * Status badges: danger (red), success (green), or default (neutral).
 *
 * Context: Renders a small pill-style span with variant styles. danger and success set
 * background and border; default uses bg-slate-800, text-primary, border-slate-600 (unified palette).
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
        ? "bg-danger-10 text-danger border border-danger"
        : success
          ? "bg-success-10 text-success border border-success"
          : "bg-slate-800 text-slate-100 border border-slate-600";

    return (
        <span className={`geometry-badge ${baseClasses} ${variantClasses}`.trim()}>
            {children}
        </span>
    );
};
