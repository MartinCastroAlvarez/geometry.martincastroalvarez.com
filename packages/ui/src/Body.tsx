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
        <div className="geometry-body min-h-screen flex flex-col flex-1 font-sans">
            <Container size={12}>
                <Container size={sideSize} />
                <Container size={middleSize}>
                    {children}
                </Container>
                <Container size={sideSize} />
            </Container>
        </div>
    );
};
