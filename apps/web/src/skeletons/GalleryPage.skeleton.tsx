/**
 * Skeleton for public Gallery view. Reuses @geometry/ui skeletons.
 * WithGalleryPageSkeleton shows skeleton when loading, otherwise renders children.
 */
import type { ReactNode } from "react";
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

export function WithGalleryPageSkeleton({ loading, children }: { loading: boolean; children: ReactNode }) {
    return loading ? <GalleryPageSkeleton /> : <>{children}</>;
}
