import React from "react";
import { Container } from "./Container";

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
    xs = false,
    sm = false,
    md = false,
    lg = false,
    xl = false,
    xxl = false,
    xxxl = false,
    left = false,
    center: _center = false,
    right = false,
    size,
    truncate = false,
    onClick = () => { },
}) => {
    void _center; // Center is the default when left and right are false
    const maxWidthStyle = size ? { maxWidth: `${size}px` } : undefined;
    const sizeClass = xs
        ? "text-xs"
        : sm
            ? "text-sm"
            : md
                ? "text-md"
                : lg
                    ? "text-lg"
                    : xl
                        ? "text-xl"
                        : xxl
                            ? "text-2xl"
                            : xxxl
                                ? "text-3xl"
                                : "text-base";
    const alignmentClass = left ? "text-left" : right ? "text-right" : "text-center";
    const truncateClass = truncate ? "truncate" : "";

    return (
        <Container center>
            <div
                onClick={onClick}
                style={maxWidthStyle}
                className={`display-block w-full mx-auto text-x-dark font-semibold font-title leading-relaxed tracking-normal ${sizeClass} ${alignmentClass} ${truncateClass}`}
            >
                {children}
            </div>
        </Container>
    );
};
