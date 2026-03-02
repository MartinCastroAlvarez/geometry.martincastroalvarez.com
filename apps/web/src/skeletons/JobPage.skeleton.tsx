/**
 * Skeleton for single Job page. Matches JobPage layout: viewer; row (badges | toolbar); title row;
 * milestones row; three inspector columns.
 */
import { Skeleton, Page, Container, TitleSkeleton, BadgeSkeleton, InspectorSkeleton, ButtonSkeleton, Toolbar, MilestonesSkeleton, useDevice } from "@geometry/ui";
import { ViewerSkeleton } from "@geometry/editor";

const INSPECTOR_HEIGHT = 480;
const VIEWER_HEIGHT = 520;

export const JobPageSkeleton = () => {
    const { isMobile } = useDevice();
    const colSize = isMobile ? 12 : 6;
    const inspectorColSize = isMobile ? 12 : 4;

    return (
        <Skeleton>
            <Page>
                <Container padded spaced>
                    <ViewerSkeleton height={VIEWER_HEIGHT} />
                </Container>
                <Container padded spaced>
                    <Container size={colSize} left={!isMobile} center={isMobile}>
                        <BadgeSkeleton width="4rem" />
                    </Container>
                    <Container size={colSize} center={isMobile} right={!isMobile}>
                        <Toolbar right={!isMobile} center={isMobile}>
                            <ButtonSkeleton sm />
                        </Toolbar>
                    </Container>
                </Container>
                <Container padded spaced>
                    <Container size={12} left={!isMobile} center={isMobile}>
                        <TitleSkeleton xl width="14rem" />
                    </Container>
                </Container>
                <Container padded spaced>
                    <Container size={12} left center>
                        <MilestonesSkeleton />
                    </Container>
                </Container>
                <Container padded spaced>
                    <Container size={12} spaced>
                        <Container size={inspectorColSize} left>
                            <Container left padded spaced>
                                <TitleSkeleton width="4rem" />
                                <InspectorSkeleton size={INSPECTOR_HEIGHT} />
                            </Container>
                        </Container>
                        <Container size={inspectorColSize} left>
                            <Container left padded spaced>
                                <TitleSkeleton width="5rem" />
                                <InspectorSkeleton size={INSPECTOR_HEIGHT} />
                            </Container>
                        </Container>
                        <Container size={inspectorColSize} left>
                            <Container left padded spaced>
                                <TitleSkeleton width="6rem" />
                                <InspectorSkeleton size={INSPECTOR_HEIGHT} />
                            </Container>
                        </Container>
                    </Container>
                </Container>
            </Page>
        </Skeleton>
    );
};
