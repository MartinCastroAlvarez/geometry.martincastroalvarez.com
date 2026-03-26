/**
 * Home page (landing): list of published art galleries in a grid of rows.
 *
 * Context: Fetches galleries via useArtGalleries from @geometry/data. Displays each in a
 * Container: Viewer (non-interactive) + title row; clicking navigates to /:id.
 * Row layout: on mobile each cell is full width (12); otherwise each row uses a random
 * pattern [4,4,4], [4,8], or [8,4] for cell sizes. Cursor pagination uses API next_token.
 */
import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import type { Gallery } from "@geometry/domain";
import { Page, Container, Title, Text, useDevice, Pagination } from "@geometry/ui";
import { Viewer } from "@geometry/editor";
import { useArtGalleries, useSession } from "@geometry/data";
import { useLocale } from "@geometry/i18n";
import { CircleDotDashed, UserStar } from "lucide-react";
import { HomePageSkeleton, HomePageGridSkeleton } from "../skeletons";
import { useCursorPagination } from "../hooks/useCursorPagination";

const DEFAULT_CELL_HEIGHT = 240;

const ROW_PATTERNS: readonly number[][] = [[4, 4, 4], [4, 8], [8, 4]];

function buildRows<T>(items: T[], isMobile: boolean): { pattern: number[]; items: T[] }[] {
    if (isMobile) {
        return items.map((item) => ({ pattern: [12], items: [item] }));
    }
    const rows: { pattern: number[]; items: T[] }[] = [];
    let i = 0;
    while (i < items.length) {
        const pattern = ROW_PATTERNS[Math.floor(Math.random() * ROW_PATTERNS.length)] as number[];
        const chunk = items.slice(i, i + pattern.length);
        rows.push({ pattern, items: chunk });
        i += pattern.length;
    }
    return rows;
}

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
                    <Container size={isMobile ? 12 : 6} right>
                        <Title sm right>
                            <span className="inline-flex items-center justify-end gap-1.5">
                                <CircleDotDashed size={16} className="shrink-0 text-slate-600 dark:text-slate-400" aria-hidden />
                                {stitchedPointsCount}
                                <UserStar size={20} className="shrink-0 text-slate-600 dark:text-slate-400" aria-hidden />
                                {guardsCount}
                            </span>
                        </Title>
                    </Container>
                </Container>
            </div>
        </div>
    );
};

export const HomePage = () => {
    const { t } = useLocale();
    const { isMobile } = useDevice();
    const { isLoading: sessionLoading } = useSession();
    const { requestNextToken, canGoPrevious, goNext, goPrev, pageIndex } = useCursorPagination();
    const {
        galleries,
        isLoading: galleriesLoading,
        isFetching: galleriesFetching,
        isPlaceholderData: galleriesPlaceholder,
    } = useArtGalleries({ limit: 20, nextToken: requestNextToken });
    const loading = sessionLoading || (galleries == null && galleriesLoading);

    const rows = useMemo(
        () => buildRows(galleries?.data ?? [], isMobile),
        [galleries?.data, isMobile]
    );

    if (loading) {
        return <HomePageSkeleton />;
    }

    if (!galleries) {
        return <HomePageSkeleton />;
    }

    if (!galleriesPlaceholder && galleries.data.length === 0 && pageIndex === 0) {
        return (
            <Page>
                <Container padded spaced>
                    <Text center>{t("home.emptyGalleries")}</Text>
                </Container>
            </Page>
        );
    }

    const showPagination = canGoPrevious || Boolean(galleries.next_token);

    return (
        <Page>
            {galleriesPlaceholder ? (
                <HomePageGridSkeleton />
            ) : (
                <Container padded spaced>
                    {rows.flatMap((row) =>
                        row.items.map((gallery, j) => (
                            <Container key={gallery.id} size={row.pattern[j]}>
                                <Cell gallery={gallery} />
                            </Container>
                        ))
                    )}
                </Container>
            )}
            {showPagination && (
                <Pagination
                    loading={galleriesFetching}
                    canGoPrevious={canGoPrevious}
                    canGoNext={Boolean(galleries.next_token)}
                    onPrevious={goPrev}
                    onNext={() => {
                        const token = galleries.next_token;
                        if (token) goNext(token);
                    }}
                />
            )}
        </Page>
    );
};
