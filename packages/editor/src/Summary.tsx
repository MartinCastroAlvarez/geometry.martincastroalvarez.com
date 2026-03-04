/**
 * Summary: 4-column stats grid (Vertices, Holes, Guards, Components/Duration) from an ArtGallery.
 * When artGallery.duration is set (e.g. published galleries), the fourth column shows humanized
 * duration instead of the number of components; vertices, holes, and guards are always shown.
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

/** Total input vertices (boundary + obstacles). Used when stitched is not yet available. */
function countInputPoints(gallery: ArtGallery): number {
    let n = gallery.boundary.points.length;
    for (const obs of gallery.obstacles) {
        n += obs.points.length;
    }
    return n;
}

/** Points count: stitched polygon vertices when available (published gallery), else boundary + obstacles. */
function countPoints(gallery: ArtGallery): number {
    if (gallery.stitched != null && gallery.stitched.points.length > 0) {
        return gallery.stitched.points.length;
    }
    return countInputPoints(gallery);
}

/** Humanize seconds for display (e.g. 1000 -> "1K", 50000 -> "50K"). Seconds are rounded down to integers. */
function humanizeDurationSeconds(seconds: number): string {
    const s = Math.floor(seconds);
    if (s >= 1e6) {
        return Math.floor(s / 1e6) + "M";
    }
    if (s >= 1000) {
        return Math.floor(s / 1000) + "K";
    }
    return String(s);
}

export const Summary: React.FC<SummaryProps> = ({ artGallery }) => {
    const { t } = useLocale();
    const { isMobile } = useDevice();
    const colSize = isMobile ? 6 : 3;

    const points = countPoints(artGallery);
    const obstacles = artGallery.obstacles.length;
    const guards = artGallery.guards.length;
    const durationMs = artGallery.duration;

    // When duration is set (e.g. published galleries), show duration in place of components only
    const hasDuration = durationMs != null && durationMs >= 0;
    const fourthLabel = hasDuration ? t("summary.seconds") : t("summary.components");

    return (
        <Container name="geometry-summary" spaced>
            <Container size={colSize} left center>
                <Stats value={points}>{t("summary.vertices")}</Stats>
            </Container>
            <Container size={colSize} left center>
                <Stats value={obstacles}>{t("summary.holes")}</Stats>
            </Container>
            <Container size={colSize} left center>
                <Stats value={guards}>{t("summary.guards")}</Stats>
            </Container>
            <Container size={colSize} left center>
                {hasDuration ? (
                    <Stats labelValue={humanizeDurationSeconds(durationMs / 1000)}>{fourthLabel}</Stats>
                ) : (
                    <Stats value={artGallery.convex_components.length}>{fourthLabel}</Stats>
                )}
            </Container>
        </Container>
    );
};

Summary.displayName = "Summary";
