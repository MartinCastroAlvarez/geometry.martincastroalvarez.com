/**
 * List item with an icon and text. Icon sits in a fixed-width column, top-aligned when text wraps.
 * Forwards the same size/alignment props as Text (xs, sm, lg, etc.).
 *
 * Example:
 *   <Bullet icon={<Minus className="size-4 text-slate-400" />} sm>Requirement one.</Bullet>
 */

import React from "react";
import { Minus } from "lucide-react";
import { Text } from "./Text";

export interface BulletProps {
    children: React.ReactNode;
    /** Icon shown in the bullet column; defaults to Minus. */
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

const defaultIcon = <Minus className="size-4 text-slate-400" aria-hidden />;

export const Bullet: React.FC<BulletProps> = ({
    children,
    icon = defaultIcon,
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
    return (
        <div className="geometry-bullet flex gap-2 items-start w-full">
            <span className="shrink-0 w-5 h-[1.25em] flex items-center justify-center" aria-hidden>
                {icon}
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
                    onClick={onClick}
                >
                    {children}
                </Text>
            </div>
        </div>
    );
};
