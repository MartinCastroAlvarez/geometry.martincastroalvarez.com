/**
 * Skeleton for public Gallery view. Reuses @geometry/ui skeletons.
 */
import { Skeleton, Container, TitleSkeleton, TextSkeleton } from "@geometry/ui";

export const GalleryPageSkeleton = () => (
    <Skeleton>
        <Container padded spaced>
            <Container center>
                <TitleSkeleton xl width="14rem" />
                <TextSkeleton md width="8rem" />
            </Container>
        </Container>
    </Skeleton>
);
