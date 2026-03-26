/**
 * Skeleton for Home (galleries list). Matches HomePage Container grid: rows of cells
 * (ViewerSkeleton + TitleSkeleton). Uses same row patterns [4,4,4], [4,8], [8,4] or full width on mobile.
 */
import { Skeleton, Page, Container, TitleSkeleton, useDevice, PaginationSkeleton } from "@geometry/ui";
import { ViewerSkeleton } from "@geometry/editor";

const HEIGHT = 240;
const CELL_COUNT = 8;

const CellSkeleton = () => (
    <div className="p-2 rounded-xl overflow-hidden">
        <ViewerSkeleton height={HEIGHT} />
        <div className="pt-2">
            <TitleSkeleton width="70%" />
        </div>
    </div>
);

/** Sizes matching HomePage row patterns: first row 4+4+4, second 4+8, third 8+4. */
const SKELETON_SIZES = [4, 4, 4, 4, 8, 4, 8, 4];

/** Grid-only skeleton for pagination transitions (same layout as HomePage). */
export const HomePageGridSkeleton = () => {
    const { isMobile } = useDevice();
    const size = isMobile ? 12 : undefined;

    return (
        <Container padded spaced>
            {Array.from({ length: CELL_COUNT }, (_, i) => (
                <Container key={i} size={size ?? SKELETON_SIZES[i]}>
                    <CellSkeleton />
                </Container>
            ))}
        </Container>
    );
};

export const HomePageSkeleton = () => {
    return (
        <Skeleton>
            <Page>
                <HomePageGridSkeleton />
                <PaginationSkeleton />
            </Page>
        </Skeleton>
    );
};
