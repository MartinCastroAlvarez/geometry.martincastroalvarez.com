/**
 * Styled text input: geometry theme with focus ring and optional className.
 *
 * Context: Forwards all native input props; adds geometry-input class and base styles
 * (bg white/5, rounded, no border/outline). Extends InputHTMLAttributes minus className.
 *
 * Example:
 *   <Input value={q} onChange={e => setQ(e.target.value)} placeholder="Search" />
 *   <Input type="password" className="mt-2" />
 */

import React from "react";

const baseClasses =
    "bg-white/5 text-white text-center rounded-lg px-3 py-2 w-full placeholder:text-white/40 outline-none border-0 shadow-none focus:!outline-none focus:!ring-0 focus:!border-0 focus:!shadow-none focus-visible:!outline-none focus-visible:!ring-0 focus-visible:!shadow-none disabled:opacity-40 disabled:cursor-not-allowed";

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "className"> {
    className?: string;
}

export const Input: React.FC<InputProps> = ({ className = "", ...props }) => {
    return (
        <input
            {...props}
            className={`geometry-input ${baseClasses} ${className}`.trim()}
        />
    );
};
