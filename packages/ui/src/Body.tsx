/**
 * Page body layout: responsive side/middle columns and full-height shell.
 *
 * Context: Uses useDevice to choose layout; on mobile/tablet middle is full width (12), sides 0.
 * On desktop, middle is 8 cols with 2-col sides. Renders inside a max-w-6xl centered wrapper
 * with geometry-body styling.
 *
 * Example:
 *   <Body>
 *     <Title>Page</Title>
 *     <Text>Content here.</Text>
 *   </Body>
 */

import React from "react";
import { Container } from "./Container";
import { useDevice } from "./useDevice";

interface BodyProps {
    children?: React.ReactNode;
}

export const Body: React.FC<BodyProps> = ({ children }) => {
    const { isMobile, isTablet } = useDevice();
    const hideSides = isMobile || isTablet;

    return (
        <div
            className="geometry-body flex flex-col flex-1 min-h-0 overflow-hidden font-sans text-slate-800 dark:text-slate-100"
            style={{ background: "var(--body-gradient)" }}
        >
            <Container>
                <Container size={hideSides ? 0 : 2} />
                <Container size={hideSides ? 12 : 8}>
                    {children}
                </Container>
            </Container>
        </div>
    );
};
