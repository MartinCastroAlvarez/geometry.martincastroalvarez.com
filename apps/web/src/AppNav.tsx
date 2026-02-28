/**
 * Top navigation: logo, create/history, locale and theme toggles, user card, login/logout.
 *
 * Shows NavSkeleton while session loads; otherwise Nav (children in Toolbar). Uses useSession, useJobs,
 * useLogout, useLocale, useTheme; tracks nav and login/logout via @geometry/analytics.
 */
import { useNavigate } from "react-router-dom";
import { Clock, Globe, Palette, Plus } from "lucide-react";
import { Theme, useTheme } from "@geometry/theme";
import { Nav, Button, Toggle, Card } from "@geometry/ui";
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
        </Nav>
    );
};
