import { useNavigate } from "react-router-dom";
import { Globe, Plus } from "lucide-react";
import { Toaster, Nav, Container, Body, Buttons, Button, Toggle } from "@geometry/ui";
import { useSession, useLogout } from "@geometry/data";
import { useLocale, Language } from "@geometry/i18n";
import { AppRoutes } from "./Routes";
import "./index.css";

const LANG_OPTIONS = [Language.EN, Language.ES];

const App = () => {
    const navigate = useNavigate();
    const { data: user } = useSession();
    const logout = useLogout();
    const { t, language, setLanguage } = useLocale();

    return (
        <Body>
            <Toaster />
            <Nav onClick={() => navigate("/")}>
                <Buttons right>
                    {user && (
                        <Button onClick={() => navigate("/jobs")} sm>
                            {t("nav.jobs")}
                        </Button>
                    )}
                    <Button onClick={() => navigate("/editor")} icon={<Plus size={14} />} sm>
                        {t("nav.create")}
                    </Button>
                    <Toggle value={language} options={LANG_OPTIONS} onChange={(v) => setLanguage(v as Language)} icon={<Globe size={14} />} sm />
                    {user ? (
                        <Button onClick={logout} sm>
                            {t("nav.logout")}
                        </Button>
                    ) : (
                        <Button onClick={logout} sm>
                            {t("nav.login")}
                        </Button>
                    )}
                </Buttons>
            </Nav>
            <Container padded spaced size={12}>
                <AppRoutes />
            </Container>
        </Body>
    );
};

export default App;
