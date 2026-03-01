/**
 * Skeleton for Home (galleries list). Matches HomePage layout: grid of cells with ViewerSkeleton
 * and TitleSkeleton. Responsive grid: 12/6/4 cols per cell.
 */
import { Skeleton, Page, Container, TitleSkeleton, useDevice } from "@geometry/ui";
import { ViewerSkeleton } from "@geometry/editor";

const VIEWER_HEIGHT = 250;
const CELL_COUNT = 6;

const CellSkeleton = () => (
    <Container padded spaced rounded left>
        <Container size={12}>
            <ViewerSkeleton height={VIEWER_HEIGHT} />
        </Container>
        <Container size={12} left>
            <TitleSkeleton width="70%" />
        </Container>
    </Container>
);

export const HomePageSkeleton = () => {
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
