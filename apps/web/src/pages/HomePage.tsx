/**
 * Home page (landing): list of published art galleries.
 *
 * Context: This is the root landing page at /. It fetches published art galleries via useArtGalleries
 * and displays them in a grid like JobsPage: each cell shows a Viewer and title; clicking navigates
 * to the gallery detail at /:id. useSession is used so the loading state is consistent (HomePageSkeleton
 * while session or galleries are loading). When galleries are empty, the page shows an empty state.
 */
import { useNavigate } from "react-router-dom";
import type { Gallery } from "@geometry/domain";
import { Page, Container, Title, Text, useDevice } from "@geometry/ui";
import { Viewer } from "@geometry/editor";
import { useArtGalleries, useSession } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { HomePageSkeleton } from "../skeletons";

const VIEWER_HEIGHT = 250;

interface CellProps {
    gallery: Gallery;
}

const Cell = ({ gallery }: CellProps) => {
    const navigate = useNavigate();
    const { t } = useLocale();
    const title =
        typeof gallery.title === "string" && gallery.title.trim()
            ? String(gallery.title)
            : t("editor.untitledGallery");

    return (
        <Container padded spaced rounded left onClick={() => navigate(`/${gallery.id}`)}>
            <Container size={12}>
                <Viewer artGallery={gallery.artGallery} size={VIEWER_HEIGHT} />
            </Container>
            <Container size={12} left>
                <Title left truncate>{title}</Title>
            </Container>
        </Container>
    );
};

export const HomePage = () => {
    const { t } = useLocale();
    const { isMobile, isTablet } = useDevice();
    const { isLoading: sessionLoading } = useSession();
    const { galleries, isLoading: galleriesLoading } = useArtGalleries({ limit: 20 });
    const loading = sessionLoading || galleriesLoading;

    if (galleries == null || loading) {
        return <HomePageSkeleton />;
    }

    if (galleries.data.length === 0) {
        return (
            <Page>
                <Container padded spaced>
                    <Text center>{t("home.emptyGalleries")}</Text>
                </Container>
            </Page>
        );
    }

    return (
        <Page>
            <Container spaced>
                {galleries.data.map((gallery) => (
                    <Container key={gallery.id} size={isMobile ? 12 : isTablet ? 6 : 4}>
                        <Cell gallery={gallery} />
                    </Container>
                ))}
            </Container>
        </Page>
    );
};
