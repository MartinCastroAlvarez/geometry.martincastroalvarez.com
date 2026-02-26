import React, { useState } from "react";
import Confirm from "./Confirm";
import { Container } from "./Container";

const useTranslation = (_ns: string) => ({ t: (key: string) => key });

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
    const { t } = useTranslation("components");
    const [showConfirm, setShowConfirm] = useState(false);

    if (!children && !icon) return null;

    const baseClasses =
        "inline-flex items-center justify-center font-medium rounded-xl transition-colors duration-200 focus:outline-none focus:ring-0 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer font-normal border-0";

    const variantClasses = "bg-neutral-700/80 text-neutral-200 hover:bg-neutral-600/90 active:bg-neutral-600";

    const getSizeClasses = (): string => {
        if (xs) return "h-6 px-1.5 text-xs";
        if (sm) return "h-7 px-1.5 text-xs";
        if (lg) return "h-12 px-4 text-base";
        return "h-10 px-3 text-sm";
    };

    const sizeClasses = getSizeClasses();
    const combinedClasses = `${baseClasses} ${variantClasses} ${sizeClasses}`.trim();

    const cloneIconWithColor = (iconElement: React.ReactNode) => {
        if (!React.isValidElement(iconElement)) return iconElement;
        const element = iconElement as React.ReactElement<{ className?: string }>;
        const existingClassName = element.props.className || "";
        return React.cloneElement(element, { className: `${existingClassName} text-neutral-200`.trim() });
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
        return t("defaultConfirmMessage");
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
