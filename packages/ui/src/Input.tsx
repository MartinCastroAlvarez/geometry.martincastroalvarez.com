/**
 * Styled text input: geometry theme with focus ring and optional className.
 *
 * Context: Forwards all native input props; adds geometry-input class and base styles
 * (bg-surface or bg-none when transparent prop is true, text-primary, placeholder:text-muted, rounded). Uses appearance-none and outline-none from app index.css. Extends InputHTMLAttributes minus className.
 *
 * Example:
 *   <Input value={q} onChange={e => setQ(e.target.value)} placeholder="Search" />
 *   <Input type="password" className="mt-2" />
 */

import React from "react";

const baseClasses =
    "appearance-none outline-none text-primary text-center rounded-lg px-3 py-2 w-full placeholder:text-muted border-0 shadow-none disabled:opacity-40 disabled:cursor-not-allowed";

const sizeClass = (lg?: boolean, xl?: boolean): string => {
    if (xl) return "text-xl";
    if (lg) return "text-lg";
    return "text-base";
};

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "className"> {
    className?: string;
    /** When true, uses bg-none (transparent background) instead of bg-surface */
    transparent?: boolean;
    /** Larger font (text-lg) */
    lg?: boolean;
    /** Extra-large font (text-xl) */
    xl?: boolean;
}

export const Input: React.FC<InputProps> = ({ className = "", transparent = false, lg, xl, ...props }) => {
    const bgClass = transparent ? "bg-none" : "bg-surface";
    return (
        <input
            {...props}
            className={`geometry-input ${bgClass} ${baseClasses} ${sizeClass(lg, xl)} ${className}`.trim()}
        />
    );
};
