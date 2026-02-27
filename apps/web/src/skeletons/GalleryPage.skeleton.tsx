/**
 * Skeleton for public Gallery view. Reuses @geometry/ui skeletons.
 */
import { Container, TitleSkeleton, TextSkeleton } from "@geometry/ui";

export const GalleryPageSkeleton = () => (
    <Container padded spaced size={12}>
        <Container center>
            <TitleSkeleton xl width="14rem" />
            <TextSkeleton md width="8rem" />
        </Container>
    </Container>
);
