/**
 * Heading text: size (xs–xxxl), alignment, optional truncate and max width.
 * When truncate is true and the content overflows, hovering shows the full text in a native tooltip.
 *
 * Context: Same size/alignment/truncate/size contract as Text but with font-semibold and
 * font-title; used for section or page titles. Renders inside a center Container.
 *
 * Example:
 *   <Title lg>Section name</Title>
 *   <Title xl center size={600}>Page title</Title>
 */

import React, { useRef, useEffect, useState } from "react";
import { Container } from "./Container";
import { Tooltip } from "./Tooltip";

interface TitleProps {
    children: React.ReactNode;
    xs?: boolean;
    sm?: boolean;
    md?: boolean;
    lg?: boolean;
    xl?: boolean;
    xxl?: boolean;
    xxxl?: boolean;
    left?: boolean;
    center?: boolean;
    right?: boolean;
    size?: number;
    truncate?: boolean;
    onClick?: React.MouseEventHandler<HTMLDivElement>;
}

export const Title: React.FC<TitleProps> = ({
    children,
    xs = false, sm = false, md = false, lg = false, xl = false, xxl = false, xxxl = false,
    left = false, center: _center = false, right = false,
    size, truncate = false,
    onClick = () => {},
}) => {
    void _center;
    const elRef = useRef<HTMLDivElement>(null);
    const [titleWhenTruncated, setTitleWhenTruncated] = useState<string | undefined>(undefined);

    useEffect(() => {
        if (!truncate || !elRef.current) return;
        const el = elRef.current;
        const truncated = el.scrollWidth > el.clientWidth || el.scrollHeight > el.clientHeight;
        setTitleWhenTruncated(truncated ? (el.textContent ?? "") : undefined);
    }, [truncate, children]);

    const maxWidthStyle = size ? { maxWidth: `${size}px` } : undefined;
    const sizeClass = xs ? "text-xs" : sm ? "text-sm" : md ? "text-md" : lg ? "text-lg" : xl ? "text-xl" : xxl ? "text-2xl" : xxxl ? "text-3xl" : "text-base";
    const alignmentClass = left ? "text-left" : right ? "text-right" : "text-center";
    const truncateClass = truncate ? "truncate" : "";

    const content = (
        <div
            ref={elRef}
            onClick={onClick}
            style={maxWidthStyle}
            className={`display-block w-full mx-auto text-slate-800 dark:text-slate-100 font-semibold font-title leading-relaxed tracking-normal ${sizeClass} ${alignmentClass} ${truncateClass}`}
        >
            {children}
        </div>
    );

    return (
        <Container center name="geometry-title">
            {truncate && titleWhenTruncated ? (
                <Tooltip title={titleWhenTruncated}>
                    <span className="block min-w-0">{content}</span>
                </Tooltip>
            ) : (
                content
            )}
        </Container>
    );
};
