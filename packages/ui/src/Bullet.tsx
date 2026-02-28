/**
 * List item with an icon and text. Icon sits in a fixed-width column, top-aligned when text wraps.
 * danger shows a red warning icon (same red as Problem); success shows a green tick; otherwise
 * uses default info icon. Forwards the same size/alignment props as Text (xs, sm, lg, etc.).
 *
 * Example:
 *   <Bullet sm>Requirement one.</Bullet>
 *   <Bullet danger sm>Validation failed.</Bullet>
 *   <Bullet success sm>OK.</Bullet>
 */

import React from "react";
import { Check, Info, TriangleAlert } from "lucide-react";
import { Text } from "./Text";

export interface BulletProps {
    children: React.ReactNode;
    /** When true, show warning icon in Problem red. */
    danger?: boolean;
    /** When true, show tick icon in green. */
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
    onClick?: React.MouseEventHandler<HTMLDivElement>;
}

const BULLET_ICON_SIZE = 15;
const defaultIcon = <Info size={BULLET_ICON_SIZE} className="shrink-0 text-muted" aria-hidden />;

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
    onClick,
}) => {
    const resolvedIcon =
        danger ? <TriangleAlert size={BULLET_ICON_SIZE} className="shrink-0 text-danger" aria-hidden /> :
        success ? <Check size={BULLET_ICON_SIZE} className="shrink-0 text-success" aria-hidden /> :
        defaultIcon;
    return (
        <div className="geometry-bullet flex gap-4 items-start w-full mt-2">
            <span className="shrink-0 w-4 min-w-4 h-[1.25em] flex items-start justify-center pt-[calc((1.25em-15px)/2)]" aria-hidden>
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
                    leading="tight"
                    muted
                    onClick={onClick}
                >
                    {children}
                </Text>
            </div>
        </div>
    );
};
