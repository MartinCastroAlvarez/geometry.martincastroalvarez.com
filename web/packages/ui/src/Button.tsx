import React, { useState } from "react";
// import { useTranslation } from "react-i18next"; // Mocking or removing if not available
// import { useTheme } from "../hooks/useTheme"; // Mocking or removing if not available
import Confirm from "./Confirm";
import { Container } from "./Container"; // Named import

// Minimal mock for hooks if they don't exist
const useTranslation = (_ns: string) => ({ t: (key: string) => key });
const useTheme = () => ({ isDarkTheme: false }); // Default to light

interface ButtonsProps {
    children: React.ReactNode;
    left?: boolean;
    center?: boolean;
    right?: boolean;
}

export const Buttons: React.FC<ButtonsProps> = ({ children, left = false, center: _center = true, right = false }) => {
    void _center;
    const justifyClass = right ? "justify-end" : left ? "justify-start" : "justify-center";

    return (
        <Container top>
            <div className={`flex items-center gap-2 w-full ${justifyClass}`}>{children}</div>
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
    iconPosition?: "left" | "right";
    confirm?: boolean | string;
    primary?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
    children,
    onClick,
    xs = false,
    sm = false,
    lg = false,
    disabled = false,
    icon,
    iconPosition = "left",
    confirm,
    primary = false,
}) => {
    const { t } = useTranslation("components");
    const [showConfirm, setShowConfirm] = useState(false);
    const { isDarkTheme } = useTheme();

    if (!children && !icon) {
        // console.warn("Button component requires either children or icon prop to be provided");
        return null;
    }

    const baseClasses = `inline-flex items-center justify-center font-medium rounded-lg transition-all duration-300 focus:outline-none focus:ring-0 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer font-normal active:scale-95 active:duration-75 hover:scale-105 hover:duration-150`;

    const getVariantClasses = (): string => {
        if (primary) {
            const textColor = isDarkTheme ? "text-x-dark" : "text-x-white";
            const hoverTextColor = isDarkTheme ? "hover:text-x-dark" : "hover:text-x-white";
            const activeTextColor = isDarkTheme ? "active:text-x-dark" : "active:text-x-white";
            return `bg-primary ${textColor} ${hoverTextColor} focus:ring-0 focus:ring-offset-0 focus:outline-none border-none ${activeTextColor}`;
        } else {
            return "bg-transparent border-none shadow-none opacity-60 hover:opacity-100 text-x-dark hover:text-x-dark focus:ring-0 focus:ring-offset-0 focus:outline-none active:ring-0 active:outline-none active:opacity-80";
        }
    };

    const variantClasses = getVariantClasses();

    const getSizeClasses = (): string => {
        if (xs) {
            return "h-6 px-2 text-xs";
        } else if (sm) {
            return "h-8 px-3 text-sm";
        } else if (lg) {
            return "h-12 px-6 text-base";
        } else {
            return "h-10 px-4 text-sm";
        }
    };

    const sizeClasses = getSizeClasses();

    const combinedClasses = `${baseClasses} ${variantClasses} ${sizeClasses}`.trim();

    const cloneIconWithColor = (iconElement: React.ReactNode) => {
        if (!React.isValidElement(iconElement)) return iconElement;

        const shouldUseWhite = primary && !isDarkTheme;
        const shouldUseDark = primary && isDarkTheme;

        let iconColorClass = "text-current";
        if (shouldUseWhite) {
            iconColorClass = "text-x-white";
        } else if (shouldUseDark) {
            iconColorClass = "text-x-dark";
        }

        const element = iconElement as React.ReactElement<{ className?: string }>;
        const existingClassName = element.props.className || "";

        return React.cloneElement(element, {
            className: `${existingClassName} ${iconColorClass}`.trim(),
        });
    };

    const handleClick = () => {
        if (confirm && !disabled) {
            setShowConfirm(true);
        } else if (onClick && !disabled) {
            onClick();
        }
    };

    const handleConfirm = () => {
        setShowConfirm(false);
        if (onClick) {
            onClick();
        }
    };

    const handleCancel = () => {
        setShowConfirm(false);
    };

    const getConfirmMessage = (): string => {
        if (typeof confirm === "string") {
            return confirm;
        }
        return t("defaultConfirmMessage");
    };

    return (
        <>
            <button
                type="button"
                onClick={handleClick}
                disabled={disabled}
                className={combinedClasses}
                style={{ outline: "none" }}
            >
                {icon && iconPosition === "left" && <span className={children ? "mr-2" : ""}>{cloneIconWithColor(icon)}</span>}
                {children && <span>{children}</span>}
                {icon && iconPosition === "right" && <span className={children ? "ml-2" : ""}>{cloneIconWithColor(icon)}</span>}
            </button>

            {confirm && (
                <Confirm isOpen={showConfirm} message={getConfirmMessage()} onConfirm={handleConfirm} onCancel={handleCancel} />
            )}
        </>
    );
};
