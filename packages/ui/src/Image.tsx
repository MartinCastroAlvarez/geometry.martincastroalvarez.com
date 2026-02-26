import React from "react";

interface ImageProps {
    src?: string;
    size?: number;
    rounded?: boolean;
}

export const Image: React.FC<ImageProps> = ({ src, size = 0, rounded = false }) => {
    if (!src || size === 0) return null;
    const style: React.CSSProperties = {
        width: size,
        height: size,
        backgroundImage: `url(${src})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
    };
    return (
        <div
            style={style}
            className={`geometry-image ${rounded ? "rounded-full overflow-hidden" : ""}`.trim()}
        />
    );
};
