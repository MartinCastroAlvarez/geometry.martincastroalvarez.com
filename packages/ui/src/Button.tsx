/**
 * Button and Toolbar: primary action UI and optional confirm dialog.
 *
 * Context: Button supports sizes (xs/sm/lg), optional icon, confirm, and disabled. When disabled,
 * the button uses reduced opacity, cursor-not-allowed, and onClick is not fired. When confirm is set,
 * click opens a Confirm modal; on confirm the original onClick runs. Toolbar wraps children in a
 * flex row with optional left/center/right alignment via Container.
 *
 * Example:
 *   <Toolbar><Button onClick={save}>Save</Button></Toolbar>
 *   <Button confirm="Delete?" onClick={onDelete}>Delete</Button>
 */

import React, { useCallback, useState } from "react";
import Confirm from "./Confirm";
import { Container } from "./Container";
import { Tooltip } from "./Tooltip";
import { useLocale } from "@geometry/i18n";
import { Theme, useTheme } from "@geometry/theme";

interface ToolbarProps {
    children: React.ReactNode;
    left?: boolean;
    center?: boolean;
    right?: boolean;
}

export const Toolbar: React.FC<ToolbarProps> = ({ children, left = false, center: _center = true, right = false }) => {
    void _center;
    const justifyClass = right ? "justify-end" : left ? "justify-start" : "justify-center";
    return (
        <Container middle spaced left={left} center={!left && !right} right={right} name="geometry-toolbar">
            <div className={`flex flex-row flex-wrap items-center gap-2 w-full ${justifyClass}`}>
                {children}
            </div>
        </Container>
    );
};

/** @deprecated Use Toolbar instead. */
export const Buttons = Toolbar;

interface ButtonProps {
    children?: React.ReactNode;
    onClick?: () => void;
    xs?: boolean;
    sm?: boolean;
    lg?: boolean;
    /** When true, uses a gradient purple carbon background. */
    primary?: boolean;
    /** When true, shows the same border as hover (e.g. for selected toolbar buttons). */
    active?: boolean;
    disabled?: boolean;
    icon?: React.ReactNode;
    confirm?: boolean | string;
    "aria-label"?: string;
    /** Optional tooltip shown on hover. */
    tooltip?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
    children,
    onClick,
    xs = false,
    sm = false,
    lg = false,
    primary = false,
    active = false,
    disabled = false,
    icon,
    confirm,
    "aria-label": ariaLabel,
    tooltip,
}) => {
    const { t } = useLocale();
    const { theme } = useTheme();
    const [showConfirm, setShowConfirm] = useState(false);

    if (!children && !icon) return null;

    const isLight = theme === Theme.Light;
    const activeBg = isLight ? "active:bg-slate-300" : "active:bg-slate-600";

    const activeBorder = isLight ? "active:border-slate-300" : "active:border-slate-600";
    const hoverBorderClass = "hover:border-primary";
    const activePropBorderClass = active ? "!border-primary" : "";
    const baseClasses = primary
        ? `appearance-none inline-flex flex-row items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200 focus:outline-none focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer border border-transparent bg-gradient-primary text-white hover:border-transparent ${activeBg} active:scale-[0.98]`
        : `appearance-none inline-flex flex-row items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200 focus:outline-none focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer border border-slate-400 dark:border-slate-600 bg-transparent text-slate-700 dark:text-slate-100 hover:text-slate-900 dark:hover:text-slate-100 ${hoverBorderClass} ${activePropBorderClass} ${activeBg} ${activeBorder} active:text-slate-900 dark:active:text-slate-100 active:scale-[0.98]`;

    const getSizeClasses = (): string => {
        if (xs) return "py-0.5 px-1.5 text-[11px]";
        if (sm) return "py-1 px-6 text-xs";
        if (lg) return "py-1 px-6 text-sm";
        return "py-1 px-6 text-xs";
    };

    const sizeClasses = getSizeClasses();
    const combinedClasses = `${baseClasses} ${sizeClasses}`.trim();
    const innerGapClass = xs ? "gap-1" : "gap-2";

    const cloneIconWithColor = (iconElement: React.ReactNode) => {
        if (!React.isValidElement(iconElement)) return iconElement;
        const element = iconElement as React.ReactElement<{ className?: string }>;
        const existingClassName = element.props.className || "";
        const iconColorClass = primary ? "text-inherit" : "text-slate-700 dark:text-slate-400";
        return React.cloneElement(element, { className: `${existingClassName} ${iconColorClass}`.trim() });
    };

    const handleClick = useCallback(() => {
        if (confirm && !disabled) setShowConfirm(true);
        else if (onClick && !disabled) onClick();
    }, [confirm, disabled, onClick]);

    const handleConfirm = useCallback(() => {
        setShowConfirm(false);
        if (onClick) onClick();
    }, [onClick]);

    const handleCancel = useCallback(() => setShowConfirm(false), []);

    const getConfirmMessage = (): string => {
        if (typeof confirm === "string") return confirm;
        return t("common.defaultConfirmMessage");
    };

    const buttonEl = (
        <button
            type="button"
            onClick={handleClick}
            disabled={disabled}
            className={`geometry-button ${combinedClasses}`.trim()}
            aria-label={ariaLabel}
        >
            <span className={`flex flex-row flex-nowrap items-center ${innerGapClass}`}>
                {icon && <span className="flex shrink-0 [&_svg]:inline-block [&_svg]:align-middle">{cloneIconWithColor(icon)}</span>}
                {children && <span>{children}</span>}
            </span>
        </button>
    );

    return (
        <>
            {tooltip ? <Tooltip title={tooltip}>{buttonEl}</Tooltip> : buttonEl}
            {confirm && (
                <Confirm isOpen={showConfirm} message={getConfirmMessage()} onConfirm={handleConfirm} onCancel={handleCancel} />
            )}
        </>
    );
};
