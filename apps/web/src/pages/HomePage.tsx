/**
 * Home page (landing): list of published art galleries in a Pinterest-style masonry.
 *
 * Context: Fetches galleries via useArtGalleries from @geometry/data. Displays each as a Pin:
 * Viewer (non-interactive) + Title only; clicking navigates to /:id. Pinterest random=true
 * assigns each Pin a size (Pinterest handles padded/spaced; no Container wrapper needed).
 */
import { useNavigate } from "react-router-dom";
import type { Gallery } from "@geometry/domain";
import { Page, Container, Title, Text, Pinterest, Pin } from "@geometry/ui";
import { Viewer } from "@geometry/editor";
import { useArtGalleries, useSession } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { HomePageSkeleton } from "../skeletons";

const DEFAULT_CELL_HEIGHT = 240;

interface CellProps {
    gallery: Gallery;
    height?: number;
}

const Cell = ({ gallery, height = DEFAULT_CELL_HEIGHT }: CellProps) => {
    const navigate = useNavigate();
    const { t } = useLocale();
    const title =
        typeof gallery.title === "string" && gallery.title.trim()
            ? String(gallery.title)
            : t("editor.untitledGallery");

    return (
        <div
            className="p-2 cursor-pointer rounded-xl overflow-hidden"
            onClick={() => navigate(`/${gallery.id}`)}
            onKeyDown={(e) => e.key === "Enter" && navigate(`/${gallery.id}`)}
            role="button"
            tabIndex={0}
            aria-label={title}
        >
            <Viewer artGallery={gallery.artGallery} size={height} />
            <div className="pt-2">
                <Title left truncate>{title}</Title>
            </div>
        </div>
    );
};

export const HomePage = () => {
    const { t } = useLocale();
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
            <Pinterest random>
                {galleries.data.map((gallery) => (
                    <Pin key={gallery.id}>
                        <Cell gallery={gallery} />
                    </Pin>
                ))}
            </Pinterest>
        </Page>
    );
};
