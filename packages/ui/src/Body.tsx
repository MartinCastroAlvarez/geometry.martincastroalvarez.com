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
    const sideSize = isMobile || isTablet ? 0 : 2;
    const middleSize = isMobile || isTablet ? 12 : 8;

    return (
        <div className="geometry-body min-h-screen flex flex-col flex-1 font-sans bg-neutral-500 text-white">
            <div className="max-w-6xl mx-auto w-full px-4 md:px-6 py-6 flex-1 flex flex-col gap-6">
                <Container size={12}>
                    <Container size={sideSize} />
                    <Container size={middleSize}>
                        {children}
                    </Container>
                    <Container size={sideSize} />
                </Container>
            </div>
        </div>
    );
};
