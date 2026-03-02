/**
 * Home page (landing): list of published art galleries in a Pinterest-style masonry.
 *
 * Context: Fetches galleries via useArtGalleries from @geometry/data. Displays each as a Pin:
 * Viewer (non-interactive) + Title only; clicking navigates to /:id. useSession keeps loading
 * state consistent; HomePageSkeleton shown while session or galleries load.
 */
import { useNavigate } from "react-router-dom";
import type { Gallery } from "@geometry/domain";
import { Page, Container, Title, Text, Pinterest, Pin } from "@geometry/ui";
import { Viewer } from "@geometry/editor";
import { useArtGalleries, useSession } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { HomePageSkeleton } from "../skeletons";

/** Variable heights for masonry effect (cycle per index). */
const HEIGHTS = [200, 260, 220, 280, 240, 300];

interface CellProps {
    gallery: Gallery;
    height: number;
}

const Cell = ({ gallery, height }: CellProps) => {
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
            <Container padded spaced>
                <Pinterest>
                    {galleries.data.map((gallery, i) => (
                        <Pin key={gallery.id}>
                            <Cell
                                gallery={gallery}
                                height={HEIGHTS[i % HEIGHTS.length]}
                            />
                        </Pin>
                    ))}
                </Pinterest>
            </Container>
        </Page>
    );
};
