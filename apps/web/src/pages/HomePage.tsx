/**
 * Home page (landing): list of published art galleries in a Pinterest-style masonry.
 *
 * Context: Fetches galleries via useArtGalleries from @geometry/data. Displays each as a Pin:
 * Viewer (non-interactive) + title row (title truncated + 4 stats); clicking navigates to /:id.
 */
import { useNavigate } from "react-router-dom";
import type { Gallery } from "@geometry/domain";
import { Page, Container, Title, Text, Pinterest, Pin, useDevice } from "@geometry/ui";
import { Viewer } from "@geometry/editor";
import { useArtGalleries, useSession } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { CircleDotDashed, UserStar } from "lucide-react";
import { HomePageSkeleton } from "../skeletons";

const DEFAULT_CELL_HEIGHT = 240;

interface CellProps {
    gallery: Gallery;
    height?: number;
}

const Cell = ({ gallery, height = DEFAULT_CELL_HEIGHT }: CellProps) => {
    const navigate = useNavigate();
    const { t } = useLocale();
    const { isMobile } = useDevice();
    const title =
        typeof gallery.title === "string" && gallery.title.trim()
            ? String(gallery.title)
            : t("editor.untitledGallery");
    const stitchedPointsCount = gallery.artGallery.stitched?.points?.length ?? 0;
    const guardsCount = gallery.artGallery.guards.length;

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
                <Container spaced>
                    <Container size={isMobile ? 12 : 6} left>
                        <Title left truncate>{title}</Title>
                    </Container>
                    <Container size={isMobile ? 12 : 6} left center>
                        <Container size={6} left center>
                            <div className="flex items-center gap-1.5">
                                <CircleDotDashed size={16} className="shrink-0 text-slate-600 dark:text-slate-400" aria-hidden />
                                <Title sm left>{stitchedPointsCount}</Title>
                            </div>
                        </Container>
                        <Container size={6} left center>
                            <div className="flex items-center gap-1.5">
                                <UserStar size={20} className="shrink-0 text-slate-600 dark:text-slate-400" aria-hidden />
                                <Title sm left>{guardsCount}</Title>
                            </div>
                        </Container>
                    </Container>
                </Container>
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
