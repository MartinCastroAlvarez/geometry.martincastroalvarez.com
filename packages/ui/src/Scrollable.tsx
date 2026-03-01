/**
 * Scrollable: a Container with {children} inside a div that has max-height and overflow-y-auto.
 * Use this when content may exceed a fixed height and should scroll instead of growing the layout.
 *
 * Example:
 *   <Scrollable height={500} padded rounded><TableRows /></Scrollable>
 *   <Scrollable height="50vh" padded spaced left><List /></Scrollable>
 */

import React from "react";
import { Container } from "./Container";
import type { ContainerProps } from "./Container";

export interface ScrollableProps extends Omit<ContainerProps, "height"> {
    /** Height of the scroll area; content scrolls on the y-axis when it exceeds this. Value in px number or CSS length (e.g. "200px", "50vh"). */
    height: number | string;
    children?: React.ReactNode;
}

export const Scrollable: React.FC<ScrollableProps> = ({
    height,
    children,
    ...containerProps
}) => (
    <Container {...containerProps}>
        <div
            className="scroll-no md:max-h-[var(--scroll-h)] md:overflow-y-auto"
            style={
                {
                    "--scroll-h":
                        typeof height === "number" ? `${height}px` : height,
                } as React.CSSProperties
            }
        >
            {children}
        </div>
    </Container>
);

Scrollable.displayName = "Scrollable";
