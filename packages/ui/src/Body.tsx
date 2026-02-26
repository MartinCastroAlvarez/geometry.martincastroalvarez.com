import React from "react";
import { Container } from "./Container";
import { useDevice } from "./useDevice";

interface BodyProps {
    children?: React.ReactNode;
}

export const Body: React.FC<BodyProps> = ({ children }) => {
    const { isMobile } = useDevice();
    const sideSize = isMobile ? 0 : 2;
    const middleSize = isMobile ? 12 : 8;

    return (
        <div className="geometry-body min-h-screen font-sans bg-dark">
            <Container padded spaced size={12}>
                <Container size={sideSize} />
                <Container size={middleSize} padded spaced>
                    {children}
                </Container>
                <Container size={sideSize} />
            </Container>
        </div>
    );
};
