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
    onClick?: React.MouseEventHandler<HTMLDivElement>;
}

export const Text: React.FC<TextProps> = ({
    children,
    xs = false, sm = false, md = false, lg = false, xl = false, xxl = false, xxxl = false,
    center = false, left: _left = false, right = false,
    size, truncate = false,
    onClick = () => {},
}) => {
    void _left;
    const maxWidthStyle = size ? { maxWidth: `${size}px` } : undefined;
    let sizeClass = xs ? "text-xs" : sm ? "text-sm" : md ? "text-md" : lg ? "text-lg" : xl ? "text-xl" : xxl ? "text-2xl" : xxxl ? "text-3xl" : "text-base";
    let alignmentClass = center ? "text-center" : right ? "text-right" : "text-left";
    const truncateClass = truncate ? "truncate" : "";

    return (
        <Container center>
            <div onClick={onClick} style={maxWidthStyle} className={`display-block w-full mx-auto text-x-dark opacity-70 font-normal leading-relaxed ${sizeClass} ${alignmentClass} ${truncateClass}`}>
                {children}
            </div>
        </Container>
    );
};
