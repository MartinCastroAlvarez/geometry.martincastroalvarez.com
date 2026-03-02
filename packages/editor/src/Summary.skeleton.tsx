/**
 * Skeleton for Summary. Same grid as Summary (4 columns: 3 on desktop/tablet, 6 on mobile).
 *
 * Example:
 *   {loading ? <SummarySkeleton /> : <Summary artGallery={gallery.artGallery} />}
 */

import React from "react";
import { Container, StatsSkeleton, useDevice } from "@geometry/ui";

export const SummarySkeleton: React.FC = () => {
    const { isMobile } = useDevice();
    const colSize = isMobile ? 6 : 3;

    return (
        <Container name="geometry-summary-skeleton" spaced>
            <Container size={colSize} left center>
                <StatsSkeleton />
            </Container>
            <Container size={colSize} left center>
                <StatsSkeleton />
            </Container>
            <Container size={colSize} left center>
                <StatsSkeleton />
            </Container>
            <Container size={colSize} left center>
                <StatsSkeleton />
            </Container>
        </Container>
    );
};

SummarySkeleton.displayName = "SummarySkeleton";
