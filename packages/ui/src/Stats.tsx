/**
 * Stats: single stat display with a big number (value or percent) and a title.
 * Either value or percent must be passed (accepts zero; null/undefined fails).
 * Optional tooltip shows on hover.
 *
 * Example:
 *   <Stats value={42}>{t("summary.points")}</Stats>
 *   <Stats percent={100} tooltip="Completion">{t("summary.guards")}</Stats>
 */

import React from "react";
import { Container } from "./Container";
import { Tooltip } from "./Tooltip";

export interface StatsProps {
    /** Numeric value to display (mutually exclusive with percent). */
    value?: number;
    /** Percentage to display with "%" suffix (mutually exclusive with value). */
    percent?: number;
    /** Optional tooltip text shown on hover. */
    tooltip?: string;
    children: React.ReactNode;
}

function hasValue(v: number | undefined | null): v is number {
    return typeof v === "number";
}

export const Stats: React.FC<StatsProps> = ({ value, percent, tooltip, children }) => {
    const hasVal = hasValue(value);
    const hasPct = hasValue(percent);
    if (!hasVal && !hasPct) {
        throw new Error("Stats: either value or percent must be passed (accepts zero, not null/undefined).");
    }
    if (hasVal && hasPct) {
        throw new Error("Stats: pass only one of value or percent.");
    }

    const display =
        hasVal ? String(value) : `${percent}%`;

    const content = (
        <Container name="geometry-stats">
            <Container size={12} center>
                <span
                    className="text-6xl md:text-7xl lg:text-8xl font-semibold font-title text-slate-800 dark:text-slate-100 tabular-nums"
                    aria-hidden
                >
                    {display}
                </span>
            </Container>
            <Container size={12} center>
                <span className="block w-full text-center font-semibold font-title text-base text-slate-500 dark:text-slate-400">
                    {children}
                </span>
            </Container>
        </Container>
    );

    if (tooltip != null && tooltip !== "") {
        return (
            <Tooltip title={tooltip}>
                <span className="inline-block w-full">{content}</span>
            </Tooltip>
        );
    }
    return content;
};

Stats.displayName = "Stats";
