/**
 * Root layout: nav, session, locale, and route outlet.
 *
 * Context: Uses useSession, useLogout, useJobs from @geometry/data; shows History link when
 * logged in and jobs list is non-empty. Nav has create (editor), language toggle, and login/logout. AppRoutes
 * render inside a padded Container. Tracks page views and nav events via @geometry/analytics.
 * AuthenticationProvider wraps App in main.tsx; useSession uses the token from it.
 */
import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Clock, Globe, Palette, Plus } from "lucide-react";
import { Theme, useTheme } from "@geometry/theme";
import { Toaster, Nav, Container, Body, Toolbar, Button, Toggle, Card } from "@geometry/ui";
import { NavSkeleton } from "./skeletons";
import { useSession, useLogout, useJobs } from "@geometry/data";
import { useLocale, Language } from "@geometry/i18n";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";
import { AppRoutes } from "./Routes";
import "./index.css";


const App = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { user, isLoading: sessionLoading } = useSession();
    const { jobs } = useJobs();
    const logout = useLogout();
    const { t, language, setLanguage } = useLocale();
    const { theme, setTheme } = useTheme();
    const { track } = useAnalytics();

    useEffect(() => {
        track({ action: GoogleAnalyticsActions.PAGE_VIEW });
        track({ action: GoogleAnalyticsActions.GEOMETRY_PAGE_VIEW, label: location.pathname || "/" });
    }, [location.pathname, track]);

    const goHome = () => {
        track({ action: GoogleAnalyticsActions.NAV_HOME, category: GoogleAnalyticsCategories.NAVIGATION });
        navigate("/");
    };
    const goHistory = () => {
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
                <Toolbar right>
                    <Button onClick={goEditor} icon={<Plus size={14} />} sm primary>
                        {t("nav.create")}
                    </Button>
                    {user && (jobs?.data?.length ?? 0) > 0 && (
                        <Button onClick={goHistory} icon={<Clock size={14} />} sm>
                            {t("nav.history")}
                        </Button>
                    )}
                    <Toggle value={language} options={Object.values(Language)} onChange={(v) => setLanguage(v as Language)} icon={<Globe size={14} />} sm />
                    <Toggle value={theme} options={Object.values(Theme)} onChange={(v) => setTheme(v as Theme)} icon={<Palette size={14} />} formatLabel={(v) => t(`theme.${v}`)} sm />
                    {user && <Card user={user} sm right rounded />}
                    {user ? (
                        <Button onClick={handleLogout} sm aria-label={t("nav.logout")}>
                            {t("nav.logout")}
                        </Button>
                    ) : (
                        <Button onClick={handleLogout} sm aria-label={t("nav.login")}>
                            {t("nav.login")}
                        </Button>
                    )}
                </Toolbar>
            </Nav>
            )}
            <Container padded spaced>
                <AppRoutes />
            </Container>
        </Body>
    );
};

export default App;
