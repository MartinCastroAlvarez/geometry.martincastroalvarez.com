/**
 * Styled text input: geometry theme with focus ring and optional className.
 *
 * Context: Forwards all native input props; adds geometry-input class and base styles
 * (bg-slate-800 or bg-none when transparent prop is true, text-primary, placeholder:text-slate-400, rounded). Uses appearance-none and outline-none from app index.css. Extends InputHTMLAttributes minus className.
 *
 * Example:
 *   <Input value={q} onChange={e => setQ(e.target.value)} placeholder="Search" />
 *   <Input type="password" className="mt-2" />
 */

import React from "react";

const baseClasses =
    "appearance-none outline-none text-slate-800 dark:text-slate-100 text-center rounded-lg py-2 w-full placeholder:text-slate-500 dark:placeholder:text-slate-400 border-0 shadow-none disabled:opacity-40 disabled:cursor-not-allowed";

const sizeClass = (lg?: boolean, xl?: boolean): string => {
    if (xl) return "text-xl";
    if (lg) return "text-lg";
    return "text-base";
};

const strongFontClasses = "font-semibold font-title leading-relaxed tracking-normal";

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "className"> {
    className?: string;
    /** When true, uses bg-none (transparent background) instead of bg-slate-800 */
    transparent?: boolean;
    /** Larger font (text-lg) */
    lg?: boolean;
    /** Extra-large font (text-xl) */
    xl?: boolean;
    /** When true, uses same font as Title (font-semibold font-title) */
    strong?: boolean;
}

export const Input: React.FC<InputProps> = ({ className = "", transparent = false, lg, xl, strong = false, ...props }) => {
    const bgClass = transparent ? "bg-none" : "bg-slate-200 dark:bg-slate-800";
    const fontClass = strong ? strongFontClasses : "";
    return (
        <input
            {...props}
            className={`geometry-input ${bgClass} ${baseClasses} ${fontClass} ${sizeClass(lg, xl)} ${className}`.trim()}
        />
    );
};
