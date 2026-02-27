/**
 * User card: label (name or email) left, avatar image right.
 *
 * Context: Single required prop User from @geometry/domain. Uses Text and Image.
 * Returns null if user or user.email is null/undefined. Uses lorem picsum when avatarUrl is null.
 * Size props (xs, sm, lg) drive both Text and Image size. Boolean left/center/right set justify.
 */
import React from "react";
import type { User } from "@geometry/domain";
import { Text } from "./Text";
import { Image } from "./Image";

const PICSUM = "https://picsum.photos/200";

function imageSizeFromSizeProps(xs?: boolean, _sm?: boolean, lg?: boolean): number {
    if (xs) return 20;
    if (lg) return 36;
    return 28; // sm default
}

export interface CardProps {
    user: User | null | undefined;
    xs?: boolean;
    sm?: boolean;
    lg?: boolean;
    left?: boolean;
    center?: boolean;
    right?: boolean;
    rounded?: boolean;
}

export const Card: React.FC<CardProps> = ({
    user,
    xs = false,
    sm = false,
    lg = false,
    left = false,
    center: _center = false,
    right = false,
    rounded = false,
}) => {
    if (user == null || user.email == null || user.email === undefined) return null;

    const label = (user.name?.trim() || user.email) ?? "";
    const src = user.avatarUrl ?? PICSUM;
    const size = imageSizeFromSizeProps(xs, sm, lg);
    const justifyClass = right ? "justify-end" : left ? "justify-start" : "justify-center";

    return (
        <div className={`flex flex-row items-center gap-2 shrink-0 ${justifyClass}`}>
            <Text xs={xs} sm={sm} lg={lg}>
                {label}
            </Text>
            <Image src={src} size={size} rounded={rounded} />
        </div>
    );
};
