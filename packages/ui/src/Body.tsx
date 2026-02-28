/**
 * Page body layout: responsive side/middle columns.
 *
 * Context: Uses useDevice to choose layout; on mobile/tablet middle is full width (12), sides 0.
 * On desktop, middle is 8 cols with 2-col sides. Content flows naturally so the whole page scrolls.
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
            className="geometry-body min-h-[100dvh] font-sans text-slate-800 dark:text-slate-100"
            style={{ background: "var(--body-gradient)" }}
        >
            <Container>
                <Container size={hideSides ? 0 : 2} />
                <Container size={hideSides ? 12 : 8}>
                    {React.Children.map(children, (child) => (
                        <div className="col-span-12">{child}</div>
                    ))}
                </Container>
            </Container>
        </div>
    );
};
