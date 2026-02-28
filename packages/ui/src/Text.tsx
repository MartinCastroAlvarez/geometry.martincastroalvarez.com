/**
 * Body text: size (xs–xxxl), alignment (left/center/right), optional truncate and max width.
 *
 * Context: Renders inside a center-aligned Container; applies text-white/60 and size/alignment
 * classes. size prop sets maxWidth in px. Empty or whitespace-only children render null.
 *
 * Example:
 *   <Text lg center>Introduction paragraph.</Text>
 *   <Text size={400} truncate>{description}</Text>
 */

import React from "react";
import { Container } from "./Container";

interface TextProps {
    children: React.ReactNode;
    xs?: boolean;
    sm?: boolean;
    md?: boolean;
    lg?: boolean;
    xl?: boolean;
    xxl?: boolean;
    xxxl?: boolean;
    center?: boolean;
    left?: boolean;
    right?: boolean;
    size?: number;
    truncate?: boolean;
    /** Line height: relaxed (default), snug, or tight. Use snug/tight in list items for better alignment with icons. */
    leading?: "relaxed" | "snug" | "tight";
    /** When true, use a more muted (lighter) text color. */
    muted?: boolean;
    onClick?: React.MouseEventHandler<HTMLDivElement>;
}

export const Text: React.FC<TextProps> = ({
    children,
    xs = false, sm = false, md = false, lg = false, xl = false, xxl = false, xxxl = false,
    center = false, left: _left = false, right = false,
    size, truncate = false,
    leading: leadingProp = "relaxed",
    muted = false,
    onClick = () => {},
}) => {
    void _left;
    if (children == null || (typeof children === "string" && children.trim() === "")) return null;
    const maxWidthStyle = size ? { maxWidth: `${size}px` } : undefined;
    let sizeClass = xs ? "text-xs" : sm ? "text-sm" : md ? "text-md" : lg ? "text-lg" : xl ? "text-xl" : xxl ? "text-2xl" : xxxl ? "text-3xl" : "text-base";
    let alignmentClass = center ? "text-center" : right ? "text-right" : "text-left";
    const truncateClass = truncate ? "truncate" : "";
    const leadingClass = leadingProp === "tight" ? "leading-tight" : leadingProp === "snug" ? "leading-snug" : "leading-relaxed";
    const colorClass = muted ? "text-muted" : "text-white/60";

    return (
        <Container center name="geometry-text">
            <div onClick={onClick} style={maxWidthStyle} className={`display-block w-full mx-auto ${colorClass} font-normal ${leadingClass} ${sizeClass} ${alignmentClass} ${truncateClass}`}>
                {children}
            </div>
        </Container>
    );
};
