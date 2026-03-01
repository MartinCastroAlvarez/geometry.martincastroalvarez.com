/**
 * Top navigation: logo, create/history, locale and theme toggles, user card, login/logout.
 *
 * Shows NavSkeleton while session loads; otherwise Nav (children in Toolbar). Uses useSession, useJobs,
 * useLogout, useLocale, useTheme; tracks nav and login/logout via @geometry/analytics.
 */
import { useNavigate } from "react-router-dom";
import { Clock } from "lucide-react";
import { Theme, useTheme } from "@geometry/theme";
import { Nav, Button, Toggle, Card, useDevice } from "@geometry/ui";
import { NavSkeleton } from "./skeletons";
import { useSession, useLogout, useJobs } from "@geometry/data";
import { useLocale, Language } from "@geometry/i18n";
import { useAnalytics, GoogleAnalyticsActions, GoogleAnalyticsCategories } from "@geometry/analytics";

export const AppNav = () => {
    const navigate = useNavigate();
    const { user, isLoading: sessionLoading } = useSession();
    const { jobs } = useJobs();
    const logout = useLogout();
    const { t, language, setLanguage } = useLocale();
    const { theme, setTheme } = useTheme();
    const { track } = useAnalytics();
    const { isMobile } = useDevice();

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

    if (sessionLoading) return <NavSkeleton />;

    return (
        <Nav onClick={goHome}>
            <Button onClick={goEditor} sm primary>
                {t("nav.create")}
            </Button>
            {user && (jobs?.data?.length ?? 0) > 0 && (
                <Button onClick={goHistory} icon={<Clock size={14} />} sm>
                    {t("nav.history")}
                </Button>
            )}
            {isMobile ? <span className="w-full basis-full block" /> : null}
            <Toggle value={language} options={Object.values(Language)} onChange={(v) => setLanguage(v as Language)} sm />
            <Toggle value={theme} options={Object.values(Theme)} onChange={(v) => setTheme(v as Theme)} formatLabel={(v) => t(`theme.${v}`)} sm />
            {isMobile ? <span className="w-full basis-full block" /> : null}
            {user && <Card user={user} sm right={!isMobile} rounded />}
            {isMobile ? <span className="w-full basis-full block" /> : null}
            {user ? (
                <Button onClick={handleLogout} sm aria-label={t("nav.logout")}>
                    {t("nav.logout")}
                </Button>
            ) : (
                <Button onClick={handleLogout} sm aria-label={t("nav.login")}>
                    {t("nav.login")}
                </Button>
            )}
        </Nav>
    );
};
