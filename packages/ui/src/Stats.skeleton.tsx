/**
 * Skeleton for Stats. Matches layout: big number bar + title bar, centered.
 *
 * Example:
 *   {loading ? <StatsSkeleton /> : <Stats value={n}>{t("summary.points")}</Stats>}
 */

import React from "react";
import { Container } from "./Container";

export const StatsSkeleton: React.FC = () => {
    return (
        <Container name="geometry-stats-skeleton">
            <Container size={12} center>
                <div
                    className="h-14 md:h-16 lg:h-20 w-24 rounded bg-slate-700 animate-pulse mx-auto"
                    aria-hidden
                />
            </Container>
            <Container size={12} center>
                <div
                    className="mt-2 h-4 w-24 rounded bg-slate-700 animate-pulse mx-auto"
                    aria-hidden
                />
            </Container>
        </Container>
    );
};

StatsSkeleton.displayName = "StatsSkeleton";
