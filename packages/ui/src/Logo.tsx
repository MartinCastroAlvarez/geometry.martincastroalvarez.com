import React from "react";
import { Image } from "./Image";

const SRC = "https://media.martincastroalvarez.com/icon/geometry/favicon.ico";

interface LogoProps {
    size?: number;
}

export const Logo: React.FC<LogoProps> = ({ size = 24 }) => {
    return <Image src={SRC} size={size} rounded />;
};
