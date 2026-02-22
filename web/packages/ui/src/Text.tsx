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
    xs = false,
    sm = false,
    md = false,
    lg = false,
    xl = false,
    xxl = false,
    xxxl = false,
    center = false,
    left: _left = false,
    right = false,
    size,
    truncate = false,
    onClick = () => { },
}) => {
    void _left; // Left is the default when center and right are false

    const maxWidthStyle = size ? { maxWidth: `${size}px` } : undefined;

    // Determine size class
    let sizeClass: string;
    if (xs) {
        sizeClass = "text-xs";
    } else if (sm) {
        sizeClass = "text-sm";
    } else if (md) {
        sizeClass = "text-md";
    } else if (lg) {
        sizeClass = "text-lg";
    } else if (xl) {
        sizeClass = "text-xl";
    } else if (xxl) {
        sizeClass = "text-2xl";
    } else if (xxxl) {
        sizeClass = "text-3xl";
    } else {
        sizeClass = "text-base";
    }

    // Determine alignment class
    let alignmentClass: string;
    if (center) {
        alignmentClass = "text-center";
    } else if (right) {
        alignmentClass = "text-right";
    } else {
        alignmentClass = "text-left";
    }

    // Determine truncate class
    const truncateClass = truncate ? "truncate" : "";

    return (
        <Container center>
            <div
                onClick={onClick}
                style={maxWidthStyle}
                className={`display-block w-full mx-auto text-x-dark opacity-70 font-normal leading-relaxed ${sizeClass} ${alignmentClass} ${truncateClass}`}
            >
                {children}
            </div>
        </Container>
    );
};
