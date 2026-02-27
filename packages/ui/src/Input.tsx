import React from "react";

const baseClasses =
    "bg-white/5 text-white border border-white/10 rounded-lg px-3 py-2 w-full placeholder:text-white/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:opacity-40 disabled:cursor-not-allowed";

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
