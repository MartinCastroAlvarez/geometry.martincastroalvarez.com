import React, { useState } from "react";
import Confirm from "./Confirm";
import { Container } from "./Container";
import { useLocale } from "@geometry/i18n";

interface ButtonsProps {
    children: React.ReactNode;
    left?: boolean;
    center?: boolean;
    right?: boolean;
}

export const Buttons: React.FC<ButtonsProps> = ({ children, left = false, center: _center = true, right = false }) => {
    void _center;

    return (
        <Container middle spaced size={12} left={left} center={!left && !right} right={right} name="geometry-buttons">
            {children}
        </Container>
    );
};

interface ButtonProps {
    children?: React.ReactNode;
    onClick?: () => void;
    xs?: boolean;
    sm?: boolean;
    lg?: boolean;
    disabled?: boolean;
    icon?: React.ReactNode;
    confirm?: boolean | string;
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
}) => {
    const { t } = useLocale();
    const [showConfirm, setShowConfirm] = useState(false);

    if (!children && !icon) return null;

    const baseClasses =
        "inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 focus:outline-none focus:ring-0 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer font-normal";

    const variantClasses =
        "bg-transparent text-x-text border border-x-border hover:bg-x-surface hover:border-x-border active:bg-x-surface-strong";

    const getSizeClasses = (): string => {
        if (xs) return "h-7 px-2 text-xs";
        if (sm) return "h-8 px-3 text-sm";
        if (lg) return "h-11 px-5 text-base";
        return "h-9 px-4 text-sm";
    };

    const sizeClasses = getSizeClasses();
    const combinedClasses = `${baseClasses} ${variantClasses} ${sizeClasses}`.trim();

    const cloneIconWithColor = (iconElement: React.ReactNode) => {
        if (!React.isValidElement(iconElement)) return iconElement;
        const element = iconElement as React.ReactElement<{ className?: string }>;
        const existingClassName = element.props.className || "";
        return React.cloneElement(element, { className: `${existingClassName} text-x-text-muted`.trim() });
    };

    const handleClick = () => {
        if (confirm && !disabled) setShowConfirm(true);
        else if (onClick && !disabled) onClick();
    };

    const handleConfirm = () => {
        setShowConfirm(false);
        if (onClick) onClick();
    };

    const handleCancel = () => setShowConfirm(false);

    const getConfirmMessage = (): string => {
        if (typeof confirm === "string") return confirm;
        return t("common.defaultConfirmMessage");
    };

    return (
        <>
            <button type="button" onClick={handleClick} disabled={disabled} className={`geometry-button ${combinedClasses}`.trim()} style={{ outline: "none" }}>
                {icon && <span className={children ? "mr-2" : ""}>{cloneIconWithColor(icon)}</span>}
                {children && <span>{children}</span>}
            </button>
            {confirm && (
                <Confirm isOpen={showConfirm} message={getConfirmMessage()} onConfirm={handleConfirm} onCancel={handleCancel} />
            )}
        </>
    );
};
