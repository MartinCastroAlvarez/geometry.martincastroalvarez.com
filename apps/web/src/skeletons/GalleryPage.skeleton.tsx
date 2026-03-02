/**
 * Skeleton for public Gallery view. Matches GalleryPage layout: Viewer (interactive height),
 * then 2 cols (desktop/tablet) or 1 (mobile): left title + muted timestamp, right Edit button.
 */
import { Skeleton, Page, Container, TitleSkeleton, TextSkeleton, ButtonSkeleton, Toolbar, useDevice } from "@geometry/ui";
import { ViewerSkeleton, SummarySkeleton } from "@geometry/editor";

const VIEWER_HEIGHT = 520;

export const GalleryPageSkeleton = () => {
    const { isMobile } = useDevice();
    const colSize = isMobile ? 12 : 6;

    return (
        <Skeleton>
            <Page>
                <Container padded spaced>
                    <ViewerSkeleton height={VIEWER_HEIGHT} />
                </Container>
                <Container padded spaced>
                    <Container size={12} left center>
                        <SummarySkeleton />
                    </Container>
                </Container>
                <Container padded spaced>
                    <Container size={colSize} left={!isMobile} center={isMobile}>
                        <Container size={12} left={!isMobile} center={isMobile}>
                            <TitleSkeleton xl width="14rem" />
                        </Container>
                        <Container size={12} left={!isMobile} center={isMobile}>
                            <TextSkeleton md width="10rem" />
                        </Container>
                    </Container>
                    <Container size={colSize} center={isMobile} right={!isMobile}>
                        <Toolbar right={!isMobile} center={isMobile}>
                            <ButtonSkeleton sm />
                        </Toolbar>
                    </Container>
                </Container>
            </Page>
        </Skeleton>
    );
};
