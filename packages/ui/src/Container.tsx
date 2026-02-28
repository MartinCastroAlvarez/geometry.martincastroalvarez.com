/**
 * Layout grid/flex container: 12-col grid, alignment, padding, and event forwarding.
 *
 * Context: size 1–12 maps to col-span; 0 renders null. With nested Containers becomes grid;
 * with middle/bottom becomes flex. Supports padded, spaced, rounded, solid and left/center/right.
 * Forwards ref and common DOM events (click, keyboard, drag, touch, etc.).
 *
 * Do not add a className prop. For custom layout/sizing, wrap Container in a plain div
 * with the desired className (e.g. <div className="w-full max-w-md"><Container>...</Container></div>).
 *
 * Example:
 *   <Container size={6} padded rounded><Content /></Container>
 *   <Container middle spaced left><Buttons>...</Buttons></Container>
 */

import React, { forwardRef } from "react";

export interface ContainerProps {
    name?: string;
    size?: number;
    padded?: boolean;
    spaced?: boolean;
    rounded?: boolean;
    solid?: boolean;
    left?: boolean;
    center?: boolean;
    right?: boolean;
    middle?: boolean;
    bottom?: boolean;
    children?: React.ReactNode;
    onMouseEnter?: React.MouseEventHandler<HTMLDivElement>;
    onMouseLeave?: React.MouseEventHandler<HTMLDivElement>;
    onMouseMove?: React.MouseEventHandler<HTMLDivElement>;
    onMouseDown?: React.MouseEventHandler<HTMLDivElement>;
    onMouseUp?: React.MouseEventHandler<HTMLDivElement>;
    onClick?: React.MouseEventHandler<HTMLDivElement>;
    onDoubleClick?: React.MouseEventHandler<HTMLDivElement>;
    onContextMenu?: React.MouseEventHandler<HTMLDivElement>;
    onFocus?: React.FocusEventHandler<HTMLDivElement>;
    onBlur?: React.FocusEventHandler<HTMLDivElement>;
    onKeyDown?: React.KeyboardEventHandler<HTMLDivElement>;
    onKeyUp?: React.KeyboardEventHandler<HTMLDivElement>;
    onKeyPress?: React.KeyboardEventHandler<HTMLDivElement>;
    onTouchStart?: React.TouchEventHandler<HTMLDivElement>;
    onTouchEnd?: React.TouchEventHandler<HTMLDivElement>;
    onTouchMove?: React.TouchEventHandler<HTMLDivElement>;
    onDragStart?: React.DragEventHandler<HTMLDivElement>;
    onDragEnd?: React.DragEventHandler<HTMLDivElement>;
    onDrag?: React.DragEventHandler<HTMLDivElement>;
    onDragEnter?: React.DragEventHandler<HTMLDivElement>;
    onDragLeave?: React.DragEventHandler<HTMLDivElement>;
    onDragOver?: React.DragEventHandler<HTMLDivElement>;
    onDrop?: React.DragEventHandler<HTMLDivElement>;
}

const colSpanClasses: Record<number, string> = {
    1: "col-span-1", 2: "col-span-2", 3: "col-span-3", 4: "col-span-4",
    5: "col-span-5", 6: "col-span-6", 7: "col-span-7", 8: "col-span-8",
    9: "col-span-9", 10: "col-span-10", 11: "col-span-11", 12: "col-span-12",
};

export const Container = forwardRef<HTMLDivElement, ContainerProps>(({
    name = "geometry-container",
    size = 12,
    padded = false,
    spaced = false,
    rounded = false,
    solid = false,
    left = false,
    center = true,
    right = false,
    middle = false,
    bottom = false,
    children,
    onMouseEnter, onMouseLeave, onMouseMove, onMouseDown, onMouseUp,
    onClick, onDoubleClick, onContextMenu,
    onFocus, onBlur, onKeyDown, onKeyUp, onKeyPress,
    onTouchStart, onTouchEnd, onTouchMove,
    onDragStart, onDragEnd, onDrag, onDragEnter, onDragLeave, onDragOver, onDrop,
}, ref) => {
    if (size < 0 || size > 12) throw new Error(`Container size must be between 0 and 12, received: ${size}`);
    if (size === 0) return null;

    const hasContainerChildren = React.Children.toArray(children).some((child) => {
        if (React.isValidElement(child)) {
            const t = child.type as React.ComponentType & { displayName?: string };
            return child.type === Container || t?.displayName === "Container" || t?.displayName === "Skeleton";
        }
        return false;
    });

    const classes: string[] = [name];
    classes.push("overflow-hidden");

    if (hasContainerChildren) {
        classes.push("grid", "grid-cols-12", "w-full");
        if (bottom) classes.push("items-end");
        else if (middle) classes.push("items-center");
        else classes.push("items-start");
    } else if (middle || bottom) {
        classes.push("flex", "flex-col", "w-full");
        if (bottom) classes.push("items-end");
        else if (middle) classes.push("items-center");
        if (left) classes.push("justify-start");
        else if (right) classes.push("justify-end");
        else if (center) classes.push("justify-center");
    }

    classes.push(colSpanClasses[size]);
    if (padded) classes.push("p-2");
    if (spaced) classes.push("gap-1");
    if (rounded) classes.push("rounded-xl");
    if (solid) classes.push("bg-slate-900", "text-slate-100");
    if (left) classes.push("text-left");
    else if (right) classes.push("text-right");
    else if (center) classes.push("text-center");

    if (onClick) classes.push("cursor-pointer");
    const finalClassName = classes.join(" ");

    return (
        <div
            ref={ref}
            className={finalClassName}
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
            {children}
        </div>
    );
});

Container.displayName = "Container";
