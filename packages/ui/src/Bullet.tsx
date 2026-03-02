/**
 * List item with an icon and text. Icon sits in a fixed-width column, top-aligned when text wraps.
 * danger shows a red warning icon (same red as Problem); success shows a circle-with-tick icon in normal text color; otherwise
 * uses default info icon. Forwards the same size/alignment props as Text (xs, sm, lg, etc.).
 *
 * Example:
 *   <Bullet sm>Requirement one.</Bullet>
 *   <Bullet danger sm>Validation failed.</Bullet>
 *   <Bullet success sm>OK.</Bullet>
 */

import React from "react";
import { CircleCheck, Info, TriangleAlert } from "lucide-react";
import { Text } from "./Text";

export interface BulletProps {
    children: React.ReactNode;
    /** When true, show warning icon in Problem red. */
    danger?: boolean;
    /** When true, show circle-with-tick icon in normal text color. */
    success?: boolean;
    xs?: boolean;
    sm?: boolean;
    md?: boolean;
    lg?: boolean;
    xl?: boolean;
    xxl?: boolean;
    xxxl?: boolean;
    center?: boolean;
    left?: boolean;
    right?: boolean;
    size?: number;
    truncate?: boolean;
    /** When true, use larger vertical spacing (e.g. for summary/validation lists). */
    spaced?: boolean;
    onClick?: React.MouseEventHandler<HTMLDivElement>;
}

const BULLET_ICON_SIZE = 15;
const defaultIcon = <Info size={BULLET_ICON_SIZE} className="shrink-0 text-slate-700 dark:text-slate-400" aria-hidden />;

export const Bullet: React.FC<BulletProps> = ({
    children,
    danger = false,
    success = false,
    xs,
    sm,
    md,
    lg,
    xl,
    xxl,
    xxxl,
    center,
    left,
    right,
    size,
    truncate,
    spaced = false,
    onClick,
}) => {
    const resolvedIcon =
        danger ? <TriangleAlert size={BULLET_ICON_SIZE} className="shrink-0 text-danger" aria-hidden /> :
        success ? <CircleCheck size={BULLET_ICON_SIZE} className="shrink-0 text-slate-700 dark:text-slate-400" aria-hidden /> :
        defaultIcon;
    return (
        <div className={`geometry-bullet flex gap-1 items-start w-full ${spaced ? "mt-2.5 mb-1.5" : "mt-1.5 mb-0.5"}`}>
            <span className="shrink-0 w-4 flex items-start justify-center pt-[calc((1.25em-15px)/2)]" aria-hidden>
                {resolvedIcon}
            </span>
            <div className="flex-1 min-w-0">
                <Text
                    xs={xs}
                    sm={sm}
                    md={md}
                    lg={lg}
                    xl={xl}
                    xxl={xxl}
                    xxxl={xxxl}
                    center={center}
                    left={left}
                    right={right}
                    size={size}
                    truncate={truncate}
                    leading="snug"
                    muted
                    onClick={onClick}
                >
                    {children}
                </Text>
            </div>
        </div>
    );
};
