/**
 * Renders a short title; hovering shows the full text in a native tooltip.
 * Use when you want a compact label with optional longer explanation on hover.
 *
 * Example:
 *   <Info title="Validation summary">{longExplanation}</Info>
 *   <Info title="Status">Detailed status message shown on hover</Info>
 */

import React from "react";

export interface InfoProps {
    /** Short text shown visibly. */
    title: React.ReactNode;
    /** Full text shown in tooltip on hover. Prefer a string for reliable tooltip content. If omitted, title is used when it is a string. */
    children?: React.ReactNode;
}

export const Info: React.FC<InfoProps> = ({ title, children }) => {
    const fullText =
        children != null && children !== ""
            ? typeof children === "string"
                ? children
                : undefined
            : typeof title === "string"
              ? title
              : undefined;
    return (
        <span title={fullText} className="cursor-help">
            {title}
        </span>
    );
};
