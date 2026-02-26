import { useNavigate, Routes, Route } from "react-router-dom";
import { Toaster, Nav, Container, Body, Buttons, Button, Toggle } from "@geometry/ui";
import { useSession, useLogout } from "@geometry/data";
import { useLocale, Language } from "@geometry/i18n";
import { HomePage, JobsPage, JobPage, GalleryPage, EditorPage } from "./pages";
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
                    <Toggle value={language} options={LANG_OPTIONS} onChange={(v) => setLanguage(v as Language)} sm />
                    {user ? (
                        <Button onClick={logout} sm>
                            {t("nav.logout")}
                        </Button>
                    ) : (
                        <Button onClick={logout} sm>
                            {t("nav.login")}
                        </Button>
                    )}
                    <Button onClick={() => navigate("/jobs")} sm>
                        {t("nav.jobs")}
                    </Button>
                    <Button onClick={() => navigate("/editor")} sm>
                        {t("nav.newArtGallery")}
                    </Button>
                </Buttons>
            </Nav>
            <Container padded spaced size={12}>
                <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/jobs" element={<JobsPage />} />
                    <Route path="/jobs/:id" element={<JobPage />} />
                    <Route path="/editor" element={<EditorPage />} />
                    <Route path="/:id" element={<GalleryPage />} />
                </Routes>
            </Container>
        </Body>
    );
};

export default App;
