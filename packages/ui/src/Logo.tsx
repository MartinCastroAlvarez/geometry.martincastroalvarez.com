/**
 * App logo: favicon image with configurable size and rounded style.
 *
 * Context: Renders Image with a fixed SRC (geometry favicon). size defaults to 24; rounded
 * is always true for the logo. Used in Nav and elsewhere for branding.
 *
 * Example:
 *   <Logo size={32} />
 */

import React from "react";
import { Image } from "./Image";

const SRC = "https://media.martincastroalvarez.com/icon/geometry/favicon.ico";

interface LogoProps {
    size?: number;
}

export const Logo: React.FC<LogoProps> = ({ size = 24 }) => {
    return <Image src={SRC} size={size} rounded />;
};
