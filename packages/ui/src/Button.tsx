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
import { useLocale } from "@geometry/i18n";

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
    disabled?: boolean;
    icon?: React.ReactNode;
    confirm?: boolean | string;
    "aria-label"?: string;
}

export const Button: React.FC<ButtonProps> = ({
    children,
    onClick,
    xs = false,
    sm = false,
    lg = false,
    disabled = false,
    icon,
    confirm,
    "aria-label": ariaLabel,
}) => {
    const { t } = useLocale();
    const [showConfirm, setShowConfirm] = useState(false);

    if (!children && !icon) return null;

    const baseClasses =
        "inline-flex flex-row items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/50 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer border-2 border-slate-300 bg-white/5 hover:bg-white/15 hover:border-slate-200 active:bg-white/20";

    const getSizeClasses = (): string => {
        if (xs) return "py-1 px-6 text-xs";
        if (sm) return "py-1 px-6 text-xs";
        if (lg) return "py-1 px-6 text-sm";
        return "py-1 px-6 text-xs";
    };

    const sizeClasses = getSizeClasses();
    const combinedClasses = `${baseClasses} ${sizeClasses}`.trim();

    const cloneIconWithColor = (iconElement: React.ReactNode) => {
        if (!React.isValidElement(iconElement)) return iconElement;
        const element = iconElement as React.ReactElement<{ className?: string }>;
        const existingClassName = element.props.className || "";
        return React.cloneElement(element, { className: `${existingClassName} text-white/70`.trim() });
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

    return (
        <>
            <button type="button" onClick={handleClick} disabled={disabled} className={`geometry-button ${combinedClasses}`.trim()} style={{ border: "2px solid rgba(148, 163, 184, 0.3)" }} aria-label={ariaLabel}>
                <span className="flex flex-row flex-nowrap items-center gap-2">
                    {icon && <span className="flex shrink-0 [&_svg]:inline-block [&_svg]:align-middle">{cloneIconWithColor(icon)}</span>}
                    {children && <span>{children}</span>}
                </span>
            </button>
            {confirm && (
                <Confirm isOpen={showConfirm} message={getConfirmMessage()} onConfirm={handleConfirm} onCancel={handleCancel} />
            )}
        </>
    );
};
