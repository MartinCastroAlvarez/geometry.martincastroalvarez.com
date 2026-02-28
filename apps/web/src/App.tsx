/**
 * Root layout: nav, route outlet. Tracks page views via @geometry/analytics.
 * AuthenticationProvider wraps App in main.tsx.
 */
import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { Toaster, Body, Container } from "@geometry/ui";
import { AppNav } from "./AppNav";
import { useAnalytics, GoogleAnalyticsActions } from "@geometry/analytics";
import { AppRoutes } from "./Routes";
import "./index.css";

const App = () => {
    const location = useLocation();
    const { track } = useAnalytics();

    useEffect(() => {
        track({ action: GoogleAnalyticsActions.PAGE_VIEW });
        track({ action: GoogleAnalyticsActions.GEOMETRY_PAGE_VIEW, label: location.pathname || "/" });
    }, [location.pathname, track]);

    return (
        <Body>
            <Toaster />
            <AppNav />
            <Container padded spaced>
                <AppRoutes />
            </Container>
        </Body>
    );
};

export default App;
