/**
 * Skeleton for Home (galleries list). Matches HomePage Pinterest layout: masonry-style column
 * grid with cells of ViewerSkeleton + TitleSkeleton (no badge). Same column count as Pinterest.
 */
import { Skeleton, Page, Container, TitleSkeleton, useDevice } from "@geometry/ui";
import { ViewerSkeleton } from "@geometry/editor";

const GAP = 8;
const HEIGHTS = [200, 260, 220, 280, 240, 300];
const CELL_COUNT = 8;

const CellSkeleton = ({ height }: { height: number }) => (
    <div
        className="geometry-pinterest-item break-inside-avoid rounded-xl overflow-hidden"
        style={{ marginBottom: GAP }}
    >
        <div className="p-2">
            <ViewerSkeleton height={height} />
            <div className="pt-2">
                <TitleSkeleton width="70%" />
            </div>
        </div>
    </div>
);

export const HomePageSkeleton = () => {
    const { isMobile, isTablet } = useDevice();
    const columnCount = isMobile ? 1 : isTablet ? 2 : 4;

    return (
        <Skeleton>
            <Page>
                <Container padded spaced>
                    <div
                        className="geometry-pinterest w-full min-w-0 max-w-full"
                        style={{
                            columnCount,
                            columnGap: GAP,
                            columnFill: "balance",
                        }}
                    >
                        {Array.from({ length: CELL_COUNT }, (_, i) => (
                            <CellSkeleton key={i} height={HEIGHTS[i % HEIGHTS.length]} />
                        ))}
                    </div>
                </Container>
            </Page>
        </Skeleton>
    );
};
