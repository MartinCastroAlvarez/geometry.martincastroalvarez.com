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
    // Mouse events
    onMouseEnter?: React.MouseEventHandler<HTMLDivElement>;
    onMouseLeave?: React.MouseEventHandler<HTMLDivElement>;
    onMouseMove?: React.MouseEventHandler<HTMLDivElement>;
    onMouseDown?: React.MouseEventHandler<HTMLDivElement>;
    onMouseUp?: React.MouseEventHandler<HTMLDivElement>;
    onClick?: React.MouseEventHandler<HTMLDivElement>;
    onDoubleClick?: React.MouseEventHandler<HTMLDivElement>;
    onContextMenu?: React.MouseEventHandler<HTMLDivElement>;
    // Focus events
    onFocus?: React.FocusEventHandler<HTMLDivElement>;
    onBlur?: React.FocusEventHandler<HTMLDivElement>;
    // Keyboard events
    onKeyDown?: React.KeyboardEventHandler<HTMLDivElement>;
    onKeyUp?: React.KeyboardEventHandler<HTMLDivElement>;
    onKeyPress?: React.KeyboardEventHandler<HTMLDivElement>;
    // Touch events
    onTouchStart?: React.TouchEventHandler<HTMLDivElement>;
    onTouchEnd?: React.TouchEventHandler<HTMLDivElement>;
    onTouchMove?: React.TouchEventHandler<HTMLDivElement>;
    // Drag events
    onDragStart?: React.DragEventHandler<HTMLDivElement>;
    onDragEnd?: React.DragEventHandler<HTMLDivElement>;
    onDrag?: React.DragEventHandler<HTMLDivElement>;
    onDragEnter?: React.DragEventHandler<HTMLDivElement>;
    onDragLeave?: React.DragEventHandler<HTMLDivElement>;
    onDragOver?: React.DragEventHandler<HTMLDivElement>;
    onDrop?: React.DragEventHandler<HTMLDivElement>;
}

const colSpanClasses: Record<number, string> = {
    1: "col-span-1",
    2: "col-span-2",
    3: "col-span-3",
    4: "col-span-4",
    5: "col-span-5",
    6: "col-span-6",
    7: "col-span-7",
    8: "col-span-8",
    9: "col-span-9",
    10: "col-span-10",
    11: "col-span-11",
    12: "col-span-12",
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
    // Mouse events
    onMouseEnter,
    onMouseLeave,
    onMouseMove,
    onMouseDown,
    onMouseUp,
    onClick,
    onDoubleClick,
    onContextMenu,
    // Focus events
    onFocus,
    onBlur,
    // Keyboard events
    onKeyDown,
    onKeyUp,
    onKeyPress,
    // Touch events
    onTouchStart,
    onTouchEnd,
    onTouchMove,
    // Drag events
    onDragStart,
    onDragEnd,
    onDrag,
    onDragEnter,
    onDragLeave,
    onDragOver,
    onDrop,
}) => {
    // Validate size prop
    if (size < 0 || size > 12) {
        throw new Error(`Container size must be between 0 and 12, received: ${size}`);
    }

    // If size is 0, return null (hide container)
    if (size === 0) {
        return null;
    }

    // Check if children include Container components
    const hasContainerChildren = React.Children.toArray(children).some((child) => {
        if (React.isValidElement(child)) {
            // Check if it's a Container component or has displayName "Container"
            // We compare against the exported component locally
            return (
                child.type === Container ||
                (child.type as React.ComponentType & { displayName?: string })?.displayName === "Container"
            );
        }
        return false;
    });

    // Build Tailwind classes
    const classes: string[] = ["time-container"];

    // Handle horizontal scrolling
    if (horizontal) {
        classes.push("overflow-x-auto", "overflow-y-hidden", "hide-scrollbar");
    } else {
        classes.push("overflow-hidden");
    }

    // If horizontal, always use flex layout
    if (horizontal) {
        classes.push("flex", "flex-nowrap", "w-full");
        // Add vertical alignment for flex items
        if (top) {
            classes.push("items-start");
        } else if (bottom) {
            classes.push("items-end");
        } else if (middle) {
            classes.push("items-center");
        }
    } else if (hasContainerChildren) {
        // If contains Container children, it's a grid container
        classes.push("grid", "grid-cols-12", "w-full");
        // Add vertical alignment for grid items
        if (top) {
            classes.push("items-start");
        } else if (bottom) {
            classes.push("items-end");
        } else if (middle) {
            classes.push("items-center");
        }
    } else {
        // For non-grid containers, add flex with vertical alignment if needed
        if (top || middle || bottom) {
            classes.push("flex");
            // Add vertical alignment
            if (top) {
                classes.push("items-start");
            } else if (bottom) {
                classes.push("items-end");
            } else if (middle) {
                classes.push("items-center");
            }
            // Add justify classes for flex alignment
            if (left) {
                classes.push("justify-start");
            } else if (right) {
                classes.push("justify-end");
            } else if (center) {
                classes.push("justify-center");
            }
        }
    }

    // Always add column span class
    classes.push(colSpanClasses[size]);

    // Add padding if padded is true - normalized to 16px (p-4) for consistent rhythm
    if (padded) {
        classes.push("p-4");
    }

    // Add gap if spaced is true - normalized to 16px (gap-4) for consistent rhythm
    if (spaced) {
        classes.push("gap-2");
    }

    // Add solid styling (like Section) if requested - with subtle border and shadow for "lift"
    if (solid) {
        classes.push("bg-x-white", "text-x-dark", "rounded-xl");
    }

    // Add text alignment classes (for text content)
    if (left) {
        classes.push("text-left");
    } else if (right) {
        classes.push("text-right");
    } else if (center) {
        classes.push("text-center");
    }

    // Build style object for background image overlay
    const backgroundImageStyle: React.CSSProperties = {};
    if (image) {
        backgroundImageStyle.backgroundImage = `url(${image})`;
        backgroundImageStyle.backgroundSize = "cover";
        backgroundImageStyle.backgroundPosition = "center";
        backgroundImageStyle.backgroundRepeat = "no-repeat";
        backgroundImageStyle.opacity = 0.1; // Make background image transparent
        backgroundImageStyle.position = "absolute";
        backgroundImageStyle.top = "0";
        backgroundImageStyle.left = "0";
        backgroundImageStyle.right = "0";
        backgroundImageStyle.bottom = "0";
        backgroundImageStyle.pointerEvents = "none"; // Allow clicks to pass through
        backgroundImageStyle.zIndex = 0;
        backgroundImageStyle.filter = "blur(10px)"; // Blur the background image
    }

    const containerStyle: React.CSSProperties = {};
    if (image) {
        containerStyle.position = "relative";
    }

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
            onFocus={onFocus}
            onBlur={onBlur}
            onKeyDown={onKeyDown}
            onKeyUp={onKeyUp}
            onKeyPress={onKeyPress}
            onTouchStart={onTouchStart}
            onTouchEnd={onTouchEnd}
            onTouchMove={onTouchMove}
            onDragStart={onDragStart}
            onDragEnd={onDragEnd}
            onDrag={onDrag}
            onDragEnter={onDragEnter}
            onDragLeave={onDragLeave}
            onDragOver={onDragOver}
            onDrop={onDrop}
        >
            {/* Transparent background image overlay */}
            {image && <div style={backgroundImageStyle} />}
            {/* Children on top (not transparent) - keep as direct children for grid layout */}
            {children}
        </div>
    );
};

Container.displayName = "Container";
