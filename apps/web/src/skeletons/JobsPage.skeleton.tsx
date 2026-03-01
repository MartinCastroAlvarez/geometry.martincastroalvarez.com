/**
 * Skeleton for Jobs list page. Matches JobsPage layout: Page > grid of cells (viewer, then title + badge).
 * Each cell mirrors Cell: Container (padded, spaced, rounded) with ViewerSkeleton, TitleSkeleton (8 cols),
 * BadgeSkeleton (4 cols). Responsive grid: 12/6/4 cols per cell.
 */
import { Skeleton, Page, Container, TitleSkeleton, BadgeSkeleton, useDevice } from "@geometry/ui";
import { ViewerSkeleton } from "@geometry/editor";

const VIEWER_HEIGHT = 250;
const CELL_COUNT = 6;

const CellSkeleton = () => (
    <Container padded spaced rounded left>
        <Container size={12}>
            <ViewerSkeleton height={VIEWER_HEIGHT} />
        </Container>
        <Container size={8} left>
            <TitleSkeleton width="70%" />
        </Container>
        <Container size={4} right>
            <BadgeSkeleton />
        </Container>
    </Container>
);

export const JobsPageSkeleton = () => {
    const { isMobile, isTablet } = useDevice();
    const size = isMobile ? 12 : isTablet ? 6 : 4;

    return (
        <Skeleton>
            <Page>
                <Container spaced>
                    {Array.from({ length: CELL_COUNT }, (_, i) => (
                        <Container key={i} size={size}>
                            <CellSkeleton />
                        </Container>
                    ))}
                </Container>
            </Page>
        </Skeleton>
    );
};
