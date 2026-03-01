import React from "react";
import { Container } from "./Container";

export interface PageProps {
    children?: React.ReactNode;
}

/**
 * Page wrapper: renders children inside a Container (padded, spaced).
 * Use as the root layout for app pages so future page-level changes can be made in one place.
 */
export const Page = ({ children }: PageProps) => (
    <Container>
        {children}
    </Container>
);

Page.displayName = "Page";
