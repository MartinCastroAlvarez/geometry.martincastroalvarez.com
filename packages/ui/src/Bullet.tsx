/**
 * List item with an icon and text. Icon sits in a fixed-width column, top-aligned when text wraps.
 * danger shows a red warning icon (same red as Problem); success shows a green tick; otherwise
 * uses icon prop or default info icon. Forwards the same size/alignment props as Text (xs, sm, lg, etc.).
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
    /** Icon shown in the bullet column when neither danger nor success; defaults to info. */
    icon?: React.ReactNode;
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

const defaultIcon = <Info className="size-4 text-slate-500 shrink-0" aria-hidden />;

export const Bullet: React.FC<BulletProps> = ({
    children,
    danger = false,
    success = false,
    icon,
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
        danger ? <TriangleAlert className="size-4 text-red-300 shrink-0" aria-hidden /> :
        success ? <Check className="size-4 text-green-300 shrink-0" aria-hidden /> :
        (icon ?? defaultIcon);
    return (
        <div className="geometry-bullet flex gap-2 items-start w-full">
            <span className="shrink-0 min-w-5 h-[1.25em] flex items-center justify-center" aria-hidden>
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
