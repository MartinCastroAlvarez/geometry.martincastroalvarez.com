/**
 * Root layout: nav, session, locale, and route outlet.
 *
 * Context: Uses useSession and useLogout from @geometry/data; shows Jobs link when
 * logged in. Nav has create (editor), language toggle, and login/logout. AppRoutes
 * render inside a padded Container. Tracks page views and nav events via @geometry/analytics.
 * AuthenticationProvider wraps App in main.tsx; useSession uses the token from it.
 */
import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Globe, Plus } from "lucide-react";
import { Toaster, Nav, NavSkeleton, Container, Body, Buttons, Button, Toggle, Card } from "@geometry/ui";
import { useSession, useLogout } from "@geometry/data";
import { useLocale, Language } from "@geometry/i18n";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { AppRoutes } from "./Routes";
import "./index.css";

const LANG_OPTIONS = [Language.EN, Language.ES];

const App = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user, isLoading: sessionLoading } = useSession();
    const logout = useLogout();
    const { t, language, setLanguage } = useLocale();
    const { track } = useAnalytics();

    useEffect(() => {
        track({ action: GoogleAnalyticsActions.PAGE_VIEW });
        track({ action: GoogleAnalyticsActions.GEOMETRY_PAGE_VIEW, label: location.pathname || "/" });
    }, [location.pathname, track]);

    const goHome = () => {
        track({ action: GoogleAnalyticsActions.NAV_HOME, category: GoogleAnalyticsCategories.NAVIGATION });
        navigate("/");
    };
    const goJobs = () => {
        track({ action: GoogleAnalyticsActions.NAV_JOBS, category: GoogleAnalyticsCategories.NAVIGATION });
        navigate("/jobs");
    };
    const goEditor = () => {
        track({ action: GoogleAnalyticsActions.NAV_EDITOR, category: GoogleAnalyticsCategories.NAVIGATION });
        navigate("/design");
    };
    const handleLogout = () => {
        track({
            action: user ? GoogleAnalyticsActions.USER_LOGOUT : GoogleAnalyticsActions.USER_LOGIN,
            category: GoogleAnalyticsCategories.USER,
        });
        logout();
    };

    return (
        <Body>
            <Toaster />
            {sessionLoading ? (
                <NavSkeleton />
            ) : (
            <Nav onClick={goHome}>
                <Buttons right>
                    <Button onClick={goEditor} icon={<Plus size={14} />} sm>
                        {t("nav.create")}
                    </Button>
                    {user && (
                        <Button onClick={goJobs} sm>
                            {t("nav.jobs")}
                        </Button>
                    )}
                    <Toggle value={language} options={LANG_OPTIONS} onChange={(v) => setLanguage(v as Language)} icon={<Globe size={14} />} sm />
                    {user && <Card user={user} sm right rounded />}
                    {user ? (
                        <Button onClick={handleLogout} sm>
                            {t("nav.logout")}
                        </Button>
                    ) : (
                        <Button onClick={handleLogout} sm>
                            {t("nav.login")}
                        </Button>
                    )}
                </Buttons>
            </Nav>
            )}
            <Container padded spaced size={12}>
                <AppRoutes />
            </Container>
        </Body>
    );
};

export default App;
