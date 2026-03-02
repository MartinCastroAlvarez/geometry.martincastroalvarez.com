/**
 * Summary: 4-column stats grid (Points, Obstacles, Guards, Components) from an ArtGallery.
 * Responsive: size 3 on desktop/tablet, 6 on mobile (2x2). Uses localized strings.
 *
 * Example:
 *   <Summary artGallery={gallery.artGallery} />
 */

import React from "react";
import type { ArtGallery } from "@geometry/domain";
import { Container, Stats, useDevice } from "@geometry/ui";
import { useLocale } from "@geometry/i18n";

export interface SummaryProps {
    artGallery: ArtGallery;
}

function countPoints(gallery: ArtGallery): number {
    let n = gallery.boundary.points.length;
    for (const obs of gallery.obstacles) {
        n += obs.points.length;
    }
    return n;
}

export const Summary: React.FC<SummaryProps> = ({ artGallery }) => {
    const { t } = useLocale();
    const { isMobile } = useDevice();
    const colSize = isMobile ? 6 : 3;

    const points = countPoints(artGallery);
    const obstacles = artGallery.obstacles.length;
    const guards = artGallery.guards.length;
    const components = artGallery.convex_components.length;

    return (
        <Container name="geometry-summary" spaced>
            <Container size={colSize} left center>
                <Stats value={points}>{t("summary.points")}</Stats>
            </Container>
            <Container size={colSize} left center>
                <Stats value={obstacles}>{t("summary.obstacles")}</Stats>
            </Container>
            <Container size={colSize} left center>
                <Stats value={guards}>{t("summary.guards")}</Stats>
            </Container>
            <Container size={colSize} left center>
                <Stats value={components}>{t("summary.components")}</Stats>
            </Container>
        </Container>
    );
};

Summary.displayName = "Summary";
