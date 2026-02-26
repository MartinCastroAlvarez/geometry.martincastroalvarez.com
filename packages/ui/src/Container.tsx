import React from "react";

interface ContainerProps {
    size?: number;
    padded?: boolean;
    spaced?: boolean;
    solid?: boolean;
    left?: boolean;
    center?: boolean;
    right?: boolean;
    top?: boolean;
    middle?: boolean;
    bottom?: boolean;
    horizontal?: boolean;
    image?: string;
    children?: React.ReactNode;
    onMouseEnter?: React.MouseEventHandler<HTMLDivElement>;
    onMouseLeave?: React.MouseEventHandler<HTMLDivElement>;
    onMouseMove?: React.MouseEventHandler<HTMLDivElement>;
    onMouseDown?: React.MouseEventHandler<HTMLDivElement>;
    onMouseUp?: React.MouseEventHandler<HTMLDivElement>;
    onClick?: React.MouseEventHandler<HTMLDivElement>;
    onDoubleClick?: React.MouseEventHandler<HTMLDivElement>;
    onContextMenu?: React.MouseEventHandler<HTMLDivElement>;
}

const colSpanClasses: Record<number, string> = {
    1: "col-span-1", 2: "col-span-2", 3: "col-span-3", 4: "col-span-4",
    5: "col-span-5", 6: "col-span-6", 7: "col-span-7", 8: "col-span-8",
    9: "col-span-9", 10: "col-span-10", 11: "col-span-11", 12: "col-span-12",
};

export const Container: React.FC<ContainerProps> = ({
    size = 12,
    padded = false,
    spaced = false,
    solid = false,
    left = false,
    center = true,
    right = false,
    top = false,
    middle = false,
    bottom = false,
    horizontal = false,
    image,
    children,
    onMouseEnter, onMouseLeave, onMouseMove, onMouseDown, onMouseUp,
    onClick, onDoubleClick, onContextMenu,
}) => {
    if (size < 0 || size > 12) throw new Error(`Container size must be between 0 and 12, received: ${size}`);
    if (size === 0) return null;

    const hasContainerChildren = React.Children.toArray(children).some((child) => {
        if (React.isValidElement(child)) {
            return child.type === Container || (child.type as React.ComponentType & { displayName?: string })?.displayName === "Container";
        }
        return false;
    });

    const classes: string[] = ["time-container"];
    if (horizontal) classes.push("overflow-x-auto", "overflow-y-hidden", "hide-scrollbar");
    else classes.push("overflow-hidden");

    if (horizontal) {
        classes.push("flex", "flex-nowrap", "w-full");
        if (top) classes.push("items-start");
        else if (bottom) classes.push("items-end");
        else if (middle) classes.push("items-center");
    } else if (hasContainerChildren) {
        classes.push("grid", "grid-cols-12", "w-full");
        if (top) classes.push("items-start");
        else if (bottom) classes.push("items-end");
        else if (middle) classes.push("items-center");
    } else if (top || middle || bottom) {
        classes.push("flex");
        if (top) classes.push("items-start");
        else if (bottom) classes.push("items-end");
        else if (middle) classes.push("items-center");
        if (left) classes.push("justify-start");
        else if (right) classes.push("justify-end");
        else if (center) classes.push("justify-center");
    }

    classes.push(colSpanClasses[size]);
    if (padded) classes.push("p-4");
    if (spaced) classes.push("gap-2");
    if (solid) classes.push("bg-x-white", "text-x-dark", "rounded-xl");
    if (left) classes.push("text-left");
    else if (right) classes.push("text-right");
    else if (center) classes.push("text-center");

    const backgroundImageStyle: React.CSSProperties = {};
    if (image) {
        backgroundImageStyle.backgroundImage = `url(${image})`;
        backgroundImageStyle.backgroundSize = "cover";
        backgroundImageStyle.backgroundPosition = "center";
        backgroundImageStyle.backgroundRepeat = "no-repeat";
        backgroundImageStyle.opacity = 0.1;
        backgroundImageStyle.position = "absolute";
        backgroundImageStyle.top = "0";
        backgroundImageStyle.left = "0";
        backgroundImageStyle.right = "0";
        backgroundImageStyle.bottom = "0";
        backgroundImageStyle.pointerEvents = "none";
        backgroundImageStyle.zIndex = 0;
        backgroundImageStyle.filter = "blur(10px)";
    }

    const containerStyle: React.CSSProperties = image ? { position: "relative" } : {};

    return (
        <div
            className={classes.join(" ")}
            style={containerStyle}
            onMouseEnter={onMouseEnter}
            onMouseLeave={onMouseLeave}
            onMouseMove={onMouseMove}
            onMouseDown={onMouseDown}
            onMouseUp={onMouseUp}
            onClick={onClick}
            onDoubleClick={onDoubleClick}
            onContextMenu={onContextMenu}
        >
            {image && <div style={backgroundImageStyle} />}
            {children}
        </div>
    );
};

Container.displayName = "Container";
