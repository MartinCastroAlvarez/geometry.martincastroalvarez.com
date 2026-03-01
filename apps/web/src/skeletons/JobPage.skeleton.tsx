/**
 * Skeleton for single Job page. Matches JobPage layout: title + toolbar row, badges row, viewer, four inspectors.
 */
import { Skeleton, Page, Container, TitleSkeleton, BadgeSkeleton, Badges, InspectorSkeleton, ButtonSkeleton, Toolbar, useDevice } from "@geometry/ui";
import { ViewerSkeleton } from "@geometry/editor";

const INSPECTOR_HEIGHT = 480;
const VIEWER_HEIGHT = 320;

export const JobPageSkeleton = () => {
    const { isMobile, isTablet } = useDevice();
    const titleSize = isMobile ? 12 : isTablet ? 6 : 8;
    const toolbarSize = isMobile ? 12 : isTablet ? 6 : 4;
    const inspectorColSize = isMobile ? 12 : 4;

    return (
        <Skeleton>
            <Page>
                <Container padded spaced>
                    <Container size={titleSize} left={!isMobile} center={isMobile}>
                        <TitleSkeleton xl width="14rem" />
                    </Container>
                    <Container size={toolbarSize} center={isMobile} right={!isMobile}>
                        <Toolbar right={!isMobile} center={isMobile}>
                            <ButtonSkeleton sm />
                        </Toolbar>
                    </Container>
                </Container>
                <Container padded spaced>
                    <Badges left={!isMobile}>
                        <BadgeSkeleton width="4rem" />
                        <BadgeSkeleton width="5rem" />
                        <BadgeSkeleton width="8rem" />
                        <BadgeSkeleton width="8rem" />
                    </Badges>
                </Container>
                <Container padded spaced>
                    <ViewerSkeleton height={VIEWER_HEIGHT} />
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
                                <TitleSkeleton width="4rem" />
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
